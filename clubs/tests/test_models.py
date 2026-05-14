import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from clubs.models import Member, Review, ReadingList


def test_book_str(book):
    assert str(book) == 'Дюна — Фрэнк Герберт'


def test_book_average_rating_no_reviews(book):
    assert book.average_rating() is None


def test_book_average_rating_with_reviews(book, member):
    Review.objects.create(book=book, member=member, rating=4, text='Хорошо')
    user2 = User.objects.create_user(username='user2', password='pass')
    member2 = Member.objects.create(user=user2)
    Review.objects.create(book=book, member=member2, rating=2, text='Не понравилось')
    assert book.average_rating() == 3.0


def test_book_average_rating_single_review(review):
    assert review.book.average_rating() == 5.0


def test_member_str(member):
    assert str(member) == 'testuser'


def test_member_linked_to_user(member, user):
    assert member.user == user
    assert user.member == member


def test_review_unique_per_book(book, member):
    Review.objects.create(book=book, member=member, rating=5, text='Первая')
    with pytest.raises(IntegrityError):
        Review.objects.create(book=book, member=member, rating=3, text='Вторая')


def test_review_rating_range(review):
    assert 1 <= review.rating <= 5


def test_reading_list_add_book(book, member):
    entry = ReadingList.objects.create(member=member, book=book, status='want')
    assert entry.status == 'want'
    assert entry.get_status_display() == 'Хочу прочитать'


def test_reading_list_unique_book(book, member):
    ReadingList.objects.create(member=member, book=book, status='want')
    with pytest.raises(IntegrityError):
        ReadingList.objects.create(member=member, book=book, status='reading')
