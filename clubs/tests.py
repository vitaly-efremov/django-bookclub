"""
Тесты для приложения clubs.

Запуск: pipenv run pytest

Мы используем pytest-django вместо стандартного unittest —
он лаконичнее и удобнее для Django-проектов.

Каждый тест:
  1. Создаёт нужные данные в тестовой БД
  2. Выполняет действие (запрос, вызов метода)
  3. Проверяет результат через assert
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Genre, Book, Member, Review, ReadingList


# ════════════════════════════════════════════
# ФИКСТУРЫ — повторно используемые тестовые данные
# ════════════════════════════════════════════

@pytest.fixture
def genre(db):
    """Создаём тестовый жанр в БД."""
    return Genre.objects.create(name='Фантастика', slug='fiction')


@pytest.fixture
def book(db, genre):
    """Создаём тестовую книгу."""
    return Book.objects.create(
        title='Дюна',
        author='Фрэнк Герберт',
        year=1965,
        genre=genre,
        description='Эпическая сага о пустынной планете Арракис.',
    )


@pytest.fixture
def another_book(db, genre):
    return Book.objects.create(
        title='Основание',
        author='Айзек Азимов',
        year=1951,
        genre=genre,
    )


@pytest.fixture
def user(db):
    """Создаём тестового пользователя Django."""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        first_name='Иван',
        last_name='Петров',
    )


@pytest.fixture
def member(db, user):
    """Создаём участника клуба, связанного с пользователем."""
    return Member.objects.create(user=user, bio='Люблю фантастику')


@pytest.fixture
def review(db, book, member):
    """Создаём тестовую рецензию."""
    return Review.objects.create(
        book=book,
        member=member,
        rating=5,
        text='Великолепная книга! Читал трижды.',
    )


# ════════════════════════════════════════════
# ТЕСТЫ МОДЕЛЕЙ
# ════════════════════════════════════════════

class TestBookModel:
    def test_str_representation(self, book):
        """Проверяем строковое представление книги."""
        assert str(book) == 'Дюна — Фрэнк Герберт'

    def test_average_rating_no_reviews(self, book):
        """Без рецензий средняя оценка должна быть None."""
        assert book.average_rating() is None

    def test_average_rating_with_reviews(self, book, member):
        """Средняя оценка считается правильно."""
        Review.objects.create(book=book, member=member, rating=4, text='Хорошо')

        # Создаём второго пользователя для второй рецензии
        user2 = User.objects.create_user(username='user2', password='pass')
        member2 = Member.objects.create(user=user2)
        Review.objects.create(book=book, member=member2, rating=2, text='Не понравилось')

        # (4 + 2) / 2 = 3.0
        assert book.average_rating() == 3.0

    def test_average_rating_single_review(self, review):
        """С одной рецензией средняя оценка равна оценке рецензии."""
        assert review.book.average_rating() == 5.0


class TestMemberModel:
    def test_str_representation(self, member, user):
        """Участник представляется именем пользователя."""
        assert str(member) == 'testuser'

    def test_member_linked_to_user(self, member, user):
        """Проверяем связь OneToOne."""
        assert member.user == user
        assert user.member == member


class TestReviewModel:
    def test_unique_review_per_book(self, db, book, member):
        """Нельзя написать две рецензии на одну книгу."""
        from django.db import IntegrityError
        Review.objects.create(book=book, member=member, rating=5, text='Первая')

        with pytest.raises(IntegrityError):
            Review.objects.create(book=book, member=member, rating=3, text='Вторая')

    def test_rating_range(self, review):
        """Оценка сохраняется в диапазоне 1–5."""
        assert 1 <= review.rating <= 5


class TestReadingList:
    def test_add_book_to_list(self, db, book, member):
        """Книга добавляется в список чтения."""
        entry = ReadingList.objects.create(
            member=member,
            book=book,
            status='want',
        )
        assert entry.status == 'want'
        assert str(entry.get_status_display()) == 'Хочу прочитать'

    def test_unique_book_in_list(self, db, book, member):
        """Одна книга не может быть дважды в одном списке."""
        from django.db import IntegrityError
        ReadingList.objects.create(member=member, book=book, status='want')

        with pytest.raises(IntegrityError):
            ReadingList.objects.create(member=member, book=book, status='reading')


# ════════════════════════════════════════════
# ТЕСТЫ VIEWS (HTTP-запросы)
# ════════════════════════════════════════════

@pytest.mark.django_db
class TestIndexView:
    def test_index_returns_200(self, client):
        """Главная страница открывается."""
        url = reverse('clubs:index')
        response = client.get(url)
        assert response.status_code == 200

    def test_index_shows_books(self, client, book):
        """На главной странице отображаются книги."""
        url = reverse('clubs:index')
        response = client.get(url)
        assert 'Дюна' in response.content.decode('utf-8')


@pytest.mark.django_db
class TestBookDetailView:
    def test_book_detail_returns_200(self, client, book):
        """Страница книги открывается."""
        url = reverse('clubs:book_detail', kwargs={'pk': book.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_book_detail_shows_title(self, client, book):
        """На странице книги отображается название."""
        url = reverse('clubs:book_detail', kwargs={'pk': book.pk})
        response = client.get(url)
        assert 'Дюна' in response.content.decode('utf-8')

    def test_book_detail_shows_reviews(self, client, book, review):
        """Рецензии отображаются на странице книги."""
        url = reverse('clubs:book_detail', kwargs={'pk': book.pk})
        response = client.get(url)
        content = response.content.decode('utf-8')
        assert 'Великолепная книга' in content

    def test_book_404_for_missing(self, client):
        """Несуществующая книга возвращает 404."""
        url = reverse('clubs:book_detail', kwargs={'pk': 99999})
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestReviewListView:
    def test_review_list_returns_200(self, client):
        url = reverse('clubs:review_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_review_list_shows_reviews(self, client, review):
        url = reverse('clubs:review_list')
        response = client.get(url)
        assert 'testuser' in response.content.decode('utf-8')


@pytest.mark.django_db
class TestMemberProfileView:
    def test_member_profile_returns_200(self, client, member):
        url = reverse('clubs:member_profile', kwargs={'username': 'testuser'})
        response = client.get(url)
        assert response.status_code == 200

    def test_member_profile_404_for_missing(self, client):
        url = reverse('clubs:member_profile', kwargs={'username': 'nobody'})
        response = client.get(url)
        assert response.status_code == 404


# ════════════════════════════════════════════
# ТЕСТЫ JSON API
# ════════════════════════════════════════════

@pytest.mark.django_db
class TestApiBooksView:
    def test_api_books_returns_json(self, client, book):
        """API возвращает JSON с правильной структурой."""
        import json
        url = reverse('clubs:api_books')
        response = client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

        data = json.loads(response.content)
        assert 'books' in data
        assert len(data['books']) == 1
        assert data['books'][0]['title'] == 'Дюна'

    def test_api_books_search(self, client, book, another_book):
        """Поиск по названию фильтрует результаты."""
        import json
        url = reverse('clubs:api_books') + '?search=Дюна'
        response = client.get(url)
        data = json.loads(response.content)
        assert len(data['books']) == 1
        assert data['books'][0]['title'] == 'Дюна'

    def test_api_books_genre_filter(self, client, book, genre):
        """Фильтрация по жанру работает."""
        import json
        url = reverse('clubs:api_books') + f'?genre={genre.slug}'
        response = client.get(url)
        data = json.loads(response.content)
        assert len(data['books']) >= 1

    def test_api_genres_returns_counts(self, client, book, genre):
        """API жанров возвращает количество книг."""
        import json
        url = reverse('clubs:api_genres')
        response = client.get(url)
        data = json.loads(response.content)
        assert 'genres' in data
        fiction = next(g for g in data['genres'] if g['slug'] == 'fiction')
        assert fiction['book_count'] == 1
