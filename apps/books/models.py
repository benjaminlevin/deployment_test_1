# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import bcrypt, re # bcrypt + regex
from django.contrib import messages # flash messages
from datetime import datetime, date, timedelta #datetime
from ..login_registration.models import User

class BookManager(models.Manager):
    
    def validate(self, request):
        post_data = request.POST
        data_check = True
        if len(post_data['new_author']) > 0:
            if len(post_data['new_author']) < 2:
                data_check = False
                messages.error(request, 'author name must contain two or more characters')
            if len(post_data['new_author']) >= 100:
                data_check = False
                messages.error(request, 'author name may not contain more than 100 characters')
            if re.match('^([A-Za-z]+\s)*([A-Za-z])*$', post_data['new_author']) is None: # allows space
                data_check = False
                messages.error(request, 'author name may only contain letters')
            author = post_data['new_author']
        else:
            author = post_data['author']
        if len(post_data['title']) < 1:
            data_check = False
            messages.error(request, 'title must contain characters')
        book_check = Book.objects.filter(title=post_data['title']).filter(author=author.upper())
        if len(book_check) > 0:
            data_check = False
            messages.error(request, 'book already entered in database')
        return data_check, author

    def new_book(self, request, author):
        post_data = request.POST
        book = Book.objects.create(
            title = post_data['title'],
            author = author.upper(),
        )
        return book

    def get_book(self, bid):
        data_check = False
        if len(Book.objects.filter(id = bid)) == 1:
            book = Book.objects.get(id = bid)
            data_check = True
        return data_check, book

    def authors(self):
        books = Book.objects.all()
        authors_init = []
        authors = []
        for book in books:
            authors_init.append(book.author.upper())
        authors_init = sorted(authors_init)
        for author in authors_init:
            if author not in authors:
                authors.append(author.upper())
            authors.sort(cmp=None)
        return authors

    # Development

    def cleardb(self):
        # delete all users
        Book.objects.all().delete()
        return self

class ReviewManager(models.Manager):

    def validate(self, request, bid):
        post_data = request.POST
        data_check = True
        book_check = Book.objects.filter(id = bid)
        user_check = User.objects.filter(id = request.session['id'])
        if len(book_check) < 1:
            data_check = False
            messages.error(request, 'invalid book')
        if len(user_check) < 1:
            data_check = False
            messages.error(request, 'invalid user')
        if len(post_data['content']) < 5:
            data_check = False
            messages.error(request, 'review must contain at least five characters')
        return data_check

    def new_review(self, request, bid):
        post_data = request.POST
        Review.objects.create(
            rating = post_data['rating'],
            content = post_data['content'],
            author = User.objects.get(id = request.session['id']),
            book = Book.objects.get(id = bid)
        )
        return self

    def book_reviews(self, book):
        reviews = Review.objects.filter(book = book).order_by('-created_at')
        for review in reviews:
            review.date = review.created_at.strftime('%B %d, %Y')
        return reviews

    def delete_validate(self, request, rid):
        data_check = False
        try:
            review = Review.objects.get(id = rid)
            if int(review.author.id) == request.session['id']:
                data_check = True
        except:
            pass
        return data_check


    # 3 most recent reviews (newest on top)
    def recent(self):
        reviews = Review.objects.all().order_by('-created_at')[:3]
        for review in reviews:
            review.date = review.created_at.strftime('%B %d, %Y')
        return reviews

    # Development

    def cleardb(self):
        # delete all users
        Review.objects.all().delete()
        return self

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100, default=' ')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BookManager()

class Review(models.Model):
    rating = models.IntegerField()
    content = models.CharField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ReviewManager()
