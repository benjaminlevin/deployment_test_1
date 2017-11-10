# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse # HttpResponse not in use
from .models import Book, Review

def index(request):
    if 'id' not in request.session:
        return redirect('/')
    context = {
        'recent_reviews' : Review.objects.recent(),
        'books' : Book.objects.all().order_by('title')
    }
    return render(request, 'books/dashboard.html', context)

def add(request):
    if 'id' not in request.session:
        return redirect('/')
    if request.method == 'POST':
        book = Book.objects.validate(request)
        if book[0] is True:
            book = Book.objects.new_book(request, book[1])
            book_id = int(book.id)
            if Review.objects.validate(request, int(book.id)) is True:
                Review.objects.new_review(request, int(book.id))
            return redirect('/books/' + str(book_id)) # TO NEW BOOK PAGE
    context = {
        'authors' : Book.objects.authors()
    }
    return render(request, 'books/new.html', context)

def book(request, bid):
    if 'id' not in request.session:
        return redirect('/')
    book = Book.objects.get_book(bid)
    if book[0] is True:
        context = {
            'book' : book[1],
            'reviews' : Review.objects.book_reviews(book = book[1])
        }
        return render(request, 'books/book.html', context)
    return redirect('/books')

def add_review(request, bid):
    if 'id' not in request.session:
        return redirect('/')
    if request.method == 'POST':
        if Review.objects.validate(request, bid) is True:
            Review.objects.new_review(request, bid)
        return redirect('/books/' + bid)
    return redirect('/books')

def delete_review(request, bid, rid):
    if 'id' not in request.session:
        return redirect('/')
    if Review.objects.delete_validate(request, rid) is True:
        Review.objects.get(id = rid).delete()
        return redirect('/books/' + bid)
    return redirect('/books')

def cleardb(request):
    Review.objects.cleardb()
    Book.objects.cleardb()
    return redirect('/')