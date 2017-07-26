from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.core.urlresolvers import reverse

import bcrypt

from .models import *

def index(request):
    if 'loggedin_id' not in request.session:
        messages.error(request, 'Must be logged in to view')
        return redirect(reverse('users:signup'))
    user = User.objects.get(id=request.session['loggedin_id'])
    return render(request, 'users/index.html', {'fav_foods': user.fav_foods.all()})

def signup(request):
    if 'loggedin_id' in request.session:
        messages.error(request, 'You are already signed up! Logout first to be able to sign up for a new account.')
        return redirect(reverse('users:index'))
    if 'first_name' not in request.session:
        request.session['first_name'] = ''
    if 'last_name' not in request.session:
        request.session['last_name'] = ''
    if 'email' not in request.session:
        request.session['email'] = ''
    if 'zipcode' not in request.session:
        request.session['zipcode'] = ''
    return render(request, 'users/signup.html')

def process_signup(request):
    if request.method == "POST":
        # FORM VALIDATION
        errors = User.objects.user_validator(request)
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect(reverse('users:signup'))
        
        # CHECK IF EMAIL IS ALREADY IN DATABASE
        found_users = User.objects.filter(email=request.POST['email'])
        if found_users.count() > 0:
            messages.error(request, 'Email already taken', extra_tags='email')
            return redirect(reverse('users:signup'))

        # ADD USER TO DATABASE
        pw_hashed = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        new_user = User.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], zipcode=request.POST['zipcode'], pw=pw_hashed)
        for food_id in request.POST.getlist('fav_food'):
            new_user.fav_foods.add(FoodCategory.objects.get(id=food_id))

        request.session['last_name'] = ''
        request.session['email'] = ''
        request.session['zipcode'] = ''
        request.session['loggedin_id'] = new_user.id
        request.session['name'] = request.POST['first_name']
        request.session['first_name'] = ''

        return redirect(reverse('users:index'))
    else:
        return redirect(reverse('users:signup'))

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        pw = request.POST['password']
        request.session['login_email'] = email

        # FORM VALIDATION
        if len(email) < 1 or len(pw) < 1:
            messages.error(request, 'Email and/or password fields cannot be blank!')
            return redirect(reverse('search:index'))
        
        # USER LOGIN
        users = User.objects.filter(email=email)
        for user in users:
            if bcrypt.checkpw(pw.encode(), user.pw.encode()):
                request.session['login_email'] = ''
                request.session['loggedin_id'] = user.id
                request.session['name'] = user.first_name
                return redirect(reverse('users:index'))
        messages.error(request, 'Wrong email/password combination!')
        return redirect(reverse('search:index'))
    else:
        return redirect(reverse('users:signup'))

def logout(request):
    if 'loggedin_id' not in request.session:
        return redirect(reverse('search:index'))
    request.session.flush()
    return redirect(reverse('search:index'))