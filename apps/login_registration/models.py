# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import bcrypt, re # bcrypt + regex
from django.contrib import messages # flash messages
from datetime import datetime, date, timedelta #datetime

class UserManager(models.Manager):
    
    # Login + Registration
    
    def validate(self, request):
        post_data = request.POST
        data_check = True
        if len(post_data['name']) < 2:
            data_check = False
            messages.error(request, 'name must contain two or more characters')
        if len(post_data['name']) >= 100:
            data_check = False
            messages.error(request, 'name may not contain more than 100 characters')
        if re.match('^([A-Za-z]+\s)*([A-Za-z])*$', post_data['name']) is None: # allows space
            data_check = False
            messages.error(request, 'name may only contain letters')

        if len(post_data['alias']) < 2:
            data_check = False
            messages.error(request, 'alias must contain two or more characters')
        if len(post_data['alias']) >= 100:
            data_check = False
            messages.error(request, 'alias may not contain more than 100 characters')
        if re.match('^[A-Za-z0-9_.-]*$', post_data['alias']) is None:
            data_check = False
            messages.error(request, 'alias may only contain letters and numbers')
        if len(User.objects.filter(alias=post_data['alias'])) > 0:
            data_check = False
            messages.error(request, 'alias already in use')

        if len(post_data['email']) > 100:
            data_check = False
            messages.error(request, 'e-mail may not contain more than 100 characters')
        if re.match('^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$', post_data['email']) is None:
            data_check = False
            messages.error(request, 'e-mail must be valid')
        if len(User.objects.filter(email=post_data['email'])) > 0:
            data_check = False
            messages.error(request, 'e-mail address already registered')

        if len(post_data['password']) < 8:
            data_check = False
            messages.error(request, 'password must contain eight or more characters')
        if post_data['password'] != post_data['confirm_password']:
            data_check = False
            messages.error(request, 'passwords must match')

        # 'error' tag messages for registration validation
        return data_check

    def register(self, request):
        post_data = request.POST
        # encode and convert entered data
        password = post_data['password'].encode(encoding='utf-8', errors='strict')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        User.objects.create(
            name = post_data['name'],
            alias = post_data['alias'],
            email = post_data['email'],
            password = hashed,
            ) 
        return self

    def login(self, request):
        post_data = request.POST
        data_check = False 
        # check db for email 
        user = User.objects.filter(email=post_data['email']) 
        if len(user) > 0: 
            # fetch user data
            user = User.objects.get(email=post_data['email'])
            # compare entered and stored passwords
            password = post_data['password'].encode(encoding='utf-8', errors='strict')
            stored = User.objects.get(email=post_data['email']).password.encode(encoding='utf-8', errors='strict')
            if bcrypt.checkpw(password, stored) is True:
                data_check=True
                # set session data
                request.session['id'] = user.id
                request.session['alias'] = user.alias
                return data_check, request
        # invalid login
        messages.warning(request, 'Invalid login')
        # 'warning' tag messages for login
        return data_check, request

    def logout(self, request):
        for data in request.session.keys(): 
            del request.session[data]
        return self

# Added Functions (REDO)

    def get_user(self, uid): # get user by ID
        data_check = False 
        # check db for id 
        user = User.objects.filter(id=uid) 
        if len(user) > 0: 
            # fetch user data
            user = User.objects.get(id=uid)
            data_check = True
        return data_check, user

    # def render_users(self):
    #     users = User.objects.all()
    #     # PLAYING
    #     # users = User.objects.raw('SELECT * FROM login_registration_User WHERE ID=7;')
    #     # users = User.objects.raw('SELECT * FROM login_registration_User;') #next functions don't work with raw query
    #     for user in users:
    #         if user.level == 9:
    #             user.user_level = 'admin'
    #         elif user.level != 9:
    #             user.user_level = 'normal'
    #         user.created_at = user.created_at.strftime('%B %d, %Y')
    #     return users

# Development

    def remove_user(self, uid):
        try:
            user = User.objects.get(id=uid)
            user.delete()
        except:
            pass
        return self

    def cleardb(self):
        # delete all users
        User.objects.all().delete()
        return self

class User(models.Model):
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
