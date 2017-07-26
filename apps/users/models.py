from __future__ import unicode_literals

from django.db import models

import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def user_validator(self, request):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        zipcode = request.POST['zipcode']
        pw = request.POST['password']
        pw_confirm = request.POST['password_confirm']
        fav_food = request.POST.getlist('fav_food')

        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        request.session['email'] = email
        request.session['zipcode'] = zipcode

        errors = {}
        if len(first_name) < 2 or len(last_name) < 2 or not first_name.isalpha() or not last_name.isalpha():
            errors['name'] = 'First and last name must be at least 2 characters and only contain letters!'
        
        if len(email) < 1:
            errors['email'] = 'Email cannot be blank!'
        elif not EMAIL_REGEX.match(email):
            errors['email'] = 'Invalid email address!'
        
        if len(zipcode) != 5 or not zipcode.isnumeric():
            errors['zipcode'] = 'Zipcode must be exactly 5 numbers'
        
        if len(pw) < 8:
            errors['pw'] = 'Password must be at least 8 characters!'
        
        if pw != pw_confirm:
            errors['pw_confirm'] = 'Passwords don\'t match!'
        
        if len(fav_food) < 1 or len(fav_food) > 5:
            errors['fav_food'] = "You must pick at least one favorite food category and no more than five!"

        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=5)
    pw = models.CharField(max_length=255)
    friends = models.ManyToManyField('self', default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    def __repr__(self):
        return "<User object: {} {}>".format(self.first_name, self.last_name)

class FoodCategory(models.Model):
    category = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name="fav_foods")
    def __repr__(self):
        return "<FoodCategory object: {}>".format(self.category)