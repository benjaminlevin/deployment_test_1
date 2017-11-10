# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse # HttpResponse not in use
from .models import User
from ..books.models import Book, Review

# Login + Registration

def index(request):
    if 'id' in request.session:
        return redirect('/books')
    return render(request, 'login_registration/index.html')

def register(request):
    if 'id' in request.session:
        return redirect('/books')
    if request.method == 'POST':
        if User.objects.validate(request) is True:
                User.objects.register(request)
                if User.objects.login(request)[0] is True:
                    # do I need to refresh request?
                    return redirect('/books')
    return redirect('/')

def login(request):
    if 'id' in request.session:
        return redirect('/books')
    if request.method == 'POST':
        if User.objects.login(request)[0] is True:
            return redirect('/books')
    return redirect('/')

def logout(request):
    User.objects.logout(request)
    return redirect('/')

# User Info

def user(request, uid):
    if 'id' not in request.session:
        return redirect('/')
    user = User.objects.get_user(uid)
    if user[0] is True:
        reviews = Review.objects.filter(author=user[1])
        context = {
            'user' : user[1],
            'review_count' : reviews.count(),
            'reviews' : reviews,
        }
        return render(request, 'login_registration/user.html', context)
    return redirect('/books')