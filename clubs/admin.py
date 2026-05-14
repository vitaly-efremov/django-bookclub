"""
Регистрация моделей в Django Admin.

Admin — встроенный интерфейс управления данными.
Здесь мы настраиваем, что показывать в списках и какие фильтры доступны.
"""

from django.contrib import admin
from .models import Genre, Book, Member, Review, ReadingList


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # slug заполняется автоматически


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'year', 'created_at']
    list_filter = ['genre', 'year']
    search_fields = ['title', 'author']
    # raw_id_fields помогает при большом количестве жанров
    autocomplete_fields = ['genre']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'joined_at']
    # Показываем поля из связанного User
    readonly_fields = ['joined_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['member', 'book', 'rating', 'created_at']
    list_filter = ['rating']
    # ⚠️ Намеренно не используем select_related — для демонстрации N+1
    # list_select_related = ['member__user', 'book']


@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    list_display = ['member', 'book', 'status', 'added_at']
    list_filter = ['status']
