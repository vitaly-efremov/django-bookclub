"""
URL-маршруты приложения clubs.

Каждая строка связывает URL-путь с функцией-view.
"""

from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    # Страницы (возвращают HTML)
    path('',                        views.index,          name='index'),
    path('books/<int:pk>/',         views.book_detail,    name='book_detail'),
    path('reviews/',                views.review_list,    name='review_list'),
    path('members/<str:username>/', views.member_profile, name='member_profile'),

    # JSON API (возвращают JSON, загружаются через JavaScript)
    path('api/books/',   views.api_books,  name='api_books'),
    path('api/genres/',  views.api_genres, name='api_genres'),
]
