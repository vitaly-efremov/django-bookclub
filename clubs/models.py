"""
Модели данных для книжного клуба.

Модели — это Python-классы, каждый из которых превращается
в таблицу в базе данных.

Схема связей:
  User (встроенный) ──1:1── Member
  Book ──< Review >── Member   (книга имеет много рецензий, участник тоже)
  Member ──M2M── Book  (через ReadingList — список "хочу прочитать")
"""

from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """
    Жанр книги.
    Отдельная модель, чтобы не хранить жанр как строку в каждой книге.
    """
    name = models.CharField('Название жанра', max_length=100, unique=True)
    slug = models.SlugField('Slug', unique=True, help_text='Используется в URL, например: fiction')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Книга — центральная модель проекта.

    Связана с Genre через ForeignKey (много книг → один жанр).
    """
    title = models.CharField('Название', max_length=300)
    author = models.CharField('Автор', max_length=200)
    year = models.PositiveIntegerField('Год издания', null=True, blank=True)
    description = models.TextField('Описание', blank=True)
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,  # если жанр удалили — просто ставим NULL
        null=True,
        blank=True,
        related_name='books',
        verbose_name='Жанр',
    )
    # Намеренно НЕТ db_index=True — для демонстрации медленного поиска
    cover_url = models.URLField('Ссылка на обложку', blank=True)
    created_at = models.DateTimeField('Добавлена', auto_now_add=True)

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        return f'{self.title} — {self.author}'

    def average_rating(self):
        """
        ⚠️  НАМЕРЕННО МЕДЛЕННЫЙ КОД для демонстрации!

        Считаем среднюю оценку в Python, загружая ВСЕ рецензии в память.
        Правильный способ: использовать аннотацию на уровне QuerySet
        через Avg() — тогда вычисление происходит в PostgreSQL.
        """
        reviews = self.reviews.all()   # SELECT * FROM reviews WHERE book_id = ?
        if not reviews:
            return None
        total = sum(r.rating for r in reviews)  # итерируем объекты Python
        return round(total / len(reviews), 1)

    def average_rating_v2(self):
        result = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(result, 1) if result is not None else None


class Member(models.Model):
    """
    Участник книжного клуба.

    Расширяет встроенного User дополнительными полями через OneToOneField.
    Это стандартный паттерн в Django — не трогать встроенную модель User,
    а создать рядом свою с доп. данными.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # удалили User → удаляется и Member
        related_name='member',
        verbose_name='Пользователь',
    )
    bio = models.TextField('О себе', blank=True)
    avatar_url = models.URLField('Аватар', blank=True)
    joined_at = models.DateTimeField('Дата вступления', auto_now_add=True)

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return self.user.username


class Review(models.Model):
    """
    Рецензия участника на книгу.

    Связывает Member и Book. Один участник может написать
    только одну рецензию на одну книгу (unique_together).
    """
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # оценки от 1 до 5

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Книга',
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Участник',
    )
    rating = models.PositiveSmallIntegerField(
        'Оценка',
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField('Текст рецензии')
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецензия'
        verbose_name_plural = 'Рецензии'
        # Один участник — одна рецензия на книгу
        unique_together = [('book', 'member')]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.member} → {self.book.title[:40]} ({self.rating}★)'


class ReadingList(models.Model):
    """
    Список чтения участника.

    Участник может добавлять книги в свой список "хочу прочитать".
    Связь ManyToMany: один участник → много книг, одна книга → много участников.
    """
    STATUS_CHOICES = [
        ('want',    'Хочу прочитать'),
        ('reading', 'Читаю сейчас'),
        ('done',    'Прочитал(а)'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='reading_list',
        verbose_name='Участник',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='in_reading_lists',
        verbose_name='Книга',
    )
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='want')
    added_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Запись в списке чтения'
        verbose_name_plural = 'Списки чтения'
        unique_together = [('member', 'book')]
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.member} — {self.book.title[:40]} [{self.get_status_display()}]'
