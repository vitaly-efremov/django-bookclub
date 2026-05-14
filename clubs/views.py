"""
Представления (views) — функции или классы, которые:
  1. Получают HTTP-запрос
  2. Работают с данными (читают из БД)
  3. Возвращают HTTP-ответ (HTML или JSON)

В этом файле намеренно оставлены неоптимальные запросы
для демонстрации на занятии по профилированию.
"""

import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Avg, Count
from django.db.models.functions import Lower

from .models import Book, Genre, Review, Member, ReadingList


# ════════════════════════════════════════════
# ГЛАВНАЯ СТРАНИЦА
# ════════════════════════════════════════════

def index(request):
    """Главная страница: список книг с базовой информацией."""
    # ⚠️  ПРОБЛЕМА N+1: получаем книги без genre
    # Для каждой книги в шаблоне будет отдельный SELECT для book.genre
    books = Book.objects.all()[:12]

    return render(request, 'clubs/index.html', {
        'books': books,
    })


# ════════════════════════════════════════════
# СТРАНИЦА КНИГИ
# ════════════════════════════════════════════

def book_detail(request, pk):
    """
    Страница отдельной книги со списком рецензий.

    ⚠️  ПРОБЛЕМА N+1:
    Загружаем рецензии без select_related('member__user').
    Для каждой рецензии в шаблоне Django делает отдельный запрос
    чтобы получить member, и ещё один — чтобы получить user.
    """
    book = get_object_or_404(Book, pk=pk)
    reviews = Review.objects.filter(book=book)  # нет select_related!

    # ⚠️  Средняя оценка считается в Python (см. метод модели),
    # а не через SQL-агрегацию
    avg_rating = book.average_rating()

    return render(request, 'clubs/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })


# ════════════════════════════════════════════
# СПИСОК РЕЦЕНЗИЙ
# ════════════════════════════════════════════

def review_list(request):
    """
    Все рецензии на сайте.

    ⚠️  САМЫЙ ПОКАЗАТЕЛЬНЫЙ N+1:
    Для каждой из N рецензий Django делает:
      - 1 запрос за review.member
      - 1 запрос за review.member.user
      - 1 запрос за review.book
    Итого: 1 (список) + N*3 запросов к БД!
    """
    reviews = Review.objects.all()   # ← нет select_related вообще

    return render(request, 'clubs/review_list.html', {
        'reviews': reviews,
    })


# ════════════════════════════════════════════
# JSON API — книги для асинхронной загрузки
# ════════════════════════════════════════════

def api_books(request):
    """
    JSON API endpoint: возвращает список книг.

    Эта view загружается на странице через JavaScript (fetch API),
    без перезагрузки страницы. Пример современного подхода:
    сервер отдаёт данные, браузер сам строит HTML.

    GET /api/books/?genre=fiction
    GET /api/books/?search=война
    """
    books = Book.objects.all()

    # Фильтрация по жанру
    genre_slug = request.GET.get('genre')
    if genre_slug:
        books = books.filter(genre__slug=genre_slug)

    # Поиск по названию
    # ⚠️  icontains на поле без индекса — полный скан таблицы (LIKE '%...%')
    search = request.GET.get('search', '').strip()
    if search:
        books = books.filter(title__icontains=search)

    # ⚠️  Снова нет select_related для genre — лишний запрос на каждую книгу
    data = []
    for book in books[:20]:
        data.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'year': book.year,
            'genre': book.genre.name if book.genre else None,  # ← доп. запрос!
            'avg_rating': book.average_rating(),               # ← ещё запросы!
            'cover_url': book.cover_url,
        })

    return JsonResponse({'books': data})


def api_genres(request):
    """JSON API: список жанров с количеством книг."""
    # Это сделано правильно — через annotate, для сравнения со студентами
    genres = Genre.objects.annotate(book_count=Count('books')).order_by('name')
    data = [
        {'slug': g.slug, 'name': g.name, 'book_count': g.book_count}
        for g in genres
    ]
    return JsonResponse({'genres': data})


# ════════════════════════════════════════════
# ПРОФИЛЬ УЧАСТНИКА
# ════════════════════════════════════════════

def member_profile(request, username):
    """Профиль участника клуба с его рецензиями и списком чтения."""
    member = get_object_or_404(Member, user__username=username)

    # ⚠️ Ещё один N+1: для каждого entry загружается book отдельным запросом
    reading_list = ReadingList.objects.filter(member=member)

    reviews = Review.objects.filter(member=member)

    return render(request, 'clubs/member_profile.html', {
        'member': member,
        'reading_list': reading_list,
        'reviews': reviews,
    })
