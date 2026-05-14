import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_index_returns_200(client):
    # Act
    response = client.get(reverse('clubs:index'))

    # Assert
    assert response.status_code == 200


def test_index_shows_books(client, book):
    # Act
    response = client.get(reverse('clubs:index'))

    # Assert
    assert 'Дюна' in response.content.decode('utf-8')


def test_book_detail_returns_200(client, book):
    # Act
    response = client.get(reverse('clubs:book_detail', kwargs={'pk': book.pk}))

    # Assert
    assert response.status_code == 200


def test_book_detail_shows_title(client, book):
    # Act
    response = client.get(reverse('clubs:book_detail', kwargs={'pk': book.pk}))

    # Assert
    assert 'Дюна' in response.content.decode('utf-8')


def test_book_detail_shows_reviews(client, review):
    # Act
    response = client.get(reverse('clubs:book_detail', kwargs={'pk': review.book.pk}))

    # Assert
    assert 'Великолепная книга' in response.content.decode('utf-8')


def test_book_detail_404_for_missing(client):
    # Act
    response = client.get(reverse('clubs:book_detail', kwargs={'pk': 99999}))

    # Assert
    assert response.status_code == 404


def test_review_list_returns_200(client):
    # Act
    response = client.get(reverse('clubs:review_list'))

    # Assert
    assert response.status_code == 200


def test_review_list_shows_reviews(client, review):
    # Act
    response = client.get(reverse('clubs:review_list'))

    # Assert
    assert 'testuser' in response.content.decode('utf-8')


def test_member_profile_returns_200(client, member):
    # Act
    response = client.get(reverse('clubs:member_profile', kwargs={'username': 'testuser'}))

    # Assert
    assert response.status_code == 200


def test_member_profile_404_for_missing(client):
    # Act
    response = client.get(reverse('clubs:member_profile', kwargs={'username': 'nobody'}))

    # Assert
    assert response.status_code == 404
