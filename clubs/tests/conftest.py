import pytest
from django.contrib.auth.models import User

from clubs.models import Genre, Book, Member, Review


@pytest.fixture
def genre(db):
    return Genre.objects.create(name='Фантастика', slug='fiction')


@pytest.fixture
def book(genre):
    return Book.objects.create(
        title='Дюна',
        author='Фрэнк Герберт',
        year=1965,
        genre=genre,
        description='Эпическая сага о пустынной планете Арракис.',
    )


@pytest.fixture
def another_book(genre):
    return Book.objects.create(
        title='Основание',
        author='Айзек Азимов',
        year=1951,
        genre=genre,
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        first_name='Иван',
        last_name='Петров',
    )


@pytest.fixture
def member(user):
    return Member.objects.create(user=user, bio='Люблю фантастику')


@pytest.fixture
def review(book, member):
    return Review.objects.create(
        book=book,
        member=member,
        rating=5,
        text='Великолепная книга! Читал трижды.',
    )
