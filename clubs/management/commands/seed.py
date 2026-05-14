"""
Команда для наполнения БД тестовыми данными.

Запуск: pipenv run python manage.py seed

Использует библиотеку Faker для генерации реалистичных данных.
Нужна для демонстрации — чтобы на странице сразу было что смотреть
и чтобы N+1 проблемы были заметны в Debug Toolbar.
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

from clubs.models import Genre, Book, Member, Review, ReadingList

fake = Faker('ru_RU')

GENRES = [
    ('Фантастика',      'fiction'),
    ('Классика',        'classic'),
    ('Детектив',        'detective'),
    ('Исторический',    'historical'),
    ('Биография',       'biography'),
]

BOOKS = [
    ('Дюна',                       'Фрэнк Герберт',      1965, 'fiction'),
    ('Основание',                  'Айзек Азимов',        1951, 'fiction'),
    ('Мастер и Маргарита',         'Михаил Булгаков',     1967, 'classic'),
    ('Преступление и наказание',   'Фёдор Достоевский',   1866, 'classic'),
    ('Шерлок Холмс',               'Артур Конан Дойл',    1887, 'detective'),
    ('Десять негритят',            'Агата Кристи',        1939, 'detective'),
    ('Война и мир',                'Лев Толстой',         1869, 'classic'),
    ('1984',                       'Джордж Оруэлл',       1949, 'fiction'),
    ('Граф Монте-Кристо',          'Александр Дюма',      1844, 'historical'),
    ('Стив Джобс',                 'Уолтер Айзексон',     2011, 'biography'),
    ('Солярис',                    'Станислав Лем',        1961, 'fiction'),
    ('Анна Каренина',              'Лев Толстой',         1877, 'classic'),
]


class Command(BaseCommand):
    help = 'Наполняет БД тестовыми данными для демонстрации'

    def handle(self, *args, **options):
        self.stdout.write('Создаём жанры...')
        genres = {}
        for name, slug in GENRES:
            genre, _ = Genre.objects.get_or_create(slug=slug, defaults={'name': name})
            genres[slug] = genre

        self.stdout.write('Создаём книги...')
        books = []
        for title, author, year, genre_slug in BOOKS:
            book, _ = Book.objects.get_or_create(
                title=title,
                defaults={
                    'author': author,
                    'year': year,
                    'genre': genres[genre_slug],
                    'description': fake.paragraph(nb_sentences=3),
                }
            )
            books.append(book)

        self.stdout.write('Создаём участников...')
        members = []
        for i in range(10):
            username = f'member{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'email': fake.email(),
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            member, _ = Member.objects.get_or_create(
                user=user,
                defaults={'bio': fake.sentence(nb_words=10)}
            )
            members.append(member)

        self.stdout.write('Создаём рецензии...')
        for member in members:
            # Каждый участник пишет 2-5 рецензий на случайные книги
            for book in random.sample(books, k=random.randint(2, 5)):
                Review.objects.get_or_create(
                    book=book,
                    member=member,
                    defaults={
                        'rating': random.randint(1, 5),
                        'text': fake.paragraph(nb_sentences=2),
                    }
                )

        self.stdout.write('Создаём списки чтения...')
        for member in members:
            for book in random.sample(books, k=random.randint(3, 7)):
                ReadingList.objects.get_or_create(
                    member=member,
                    book=book,
                    defaults={'status': random.choice(['want', 'reading', 'done'])}
                )

        # Создаём суперпользователя для Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Создан superuser: admin / admin123'))

        self.stdout.write(self.style.SUCCESS(
            f'Готово! {len(books)} книг, {len(members)} участников.'
        ))
