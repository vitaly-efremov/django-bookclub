import json

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_api_books_returns_json(client, book):
    response = client.get(reverse('clubs:api_books'))
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/json'
    data = json.loads(response.content)
    assert 'books' in data
    assert len(data['books']) == 1
    assert data['books'][0]['title'] == 'Дюна'


def test_api_books_search(client, book, another_book):
    response = client.get(reverse('clubs:api_books') + '?search=Дюна')
    data = json.loads(response.content)
    assert len(data['books']) == 1
    assert data['books'][0]['title'] == 'Дюна'


def test_api_books_genre_filter(client, book, genre):
    response = client.get(reverse('clubs:api_books') + f'?genre={genre.slug}')
    data = json.loads(response.content)
    assert len(data['books']) >= 1


def test_api_genres_returns_counts(client, book, genre):
    response = client.get(reverse('clubs:api_genres'))
    data = json.loads(response.content)
    assert 'genres' in data
    fiction = next(g for g in data['genres'] if g['slug'] == 'fiction')
    assert fiction['book_count'] == 1
