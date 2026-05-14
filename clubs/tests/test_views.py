import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_index_returns_200(client):
    response = client.get(reverse('clubs:index'))
    assert response.status_code == 200


def test_index_shows_books(client, book):
    response = client.get(reverse('clubs:index'))
    assert 'Дюна' in response.content.decode('utf-8')


def test_book_detail_returns_200(client, book):
    response = client.get(reverse('clubs:book_detail', kwargs={'pk': book.pk}))
    assert response.status_code == 200


def test_book_detail_shows_title(client, book):
    response = client.get(reverse('clubs:book_detail', kwargs={'pk': book.pk}))
    assert 'Дюна' in response.content.decode('utf-8')


def test_book_detail_shows_reviews(client, review):
    response = client.get(reverse('clubs:book_detail', kwargs={'pk': review.book.pk}))
    assert 'Великолепная книга' in response.content.decode('utf-8')


def test_book_detail_404_for_missing(client):
    response = client.get(reverse('clubs:book_detail', kwargs={'pk': 99999}))
    assert response.status_code == 404


def test_review_list_returns_200(client):
    response = client.get(reverse('clubs:review_list'))
    assert response.status_code == 200


def test_review_list_shows_reviews(client, review):
    response = client.get(reverse('clubs:review_list'))
    assert 'testuser' in response.content.decode('utf-8')


def test_member_profile_returns_200(client, member):
    response = client.get(reverse('clubs:member_profile', kwargs={'username': 'testuser'}))
    assert response.status_code == 200


def test_member_profile_404_for_missing(client):
    response = client.get(reverse('clubs:member_profile', kwargs={'username': 'nobody'}))
    assert response.status_code == 404
