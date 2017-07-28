from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core import serializers

import bcrypt
import json

from .models import *

def index(request):
    if 'loggedin_id' not in request.session:
        messages.error(request, 'Must be logged in to view')
        return redirect(reverse('users:signup'))
    request.session['term'] = ''
    current_user = User.objects.get(id=request.session['loggedin_id'])
    all_friends = current_user.friends.all()
    current_group = current_user.current_group.all().values('id')
    friends = all_friends.exclude(id__in=current_group).order_by("last_name")
    context = {
        'friends': friends,
        'members': current_user.current_group.all().exclude(id=current_user.id).order_by("last_name"),
        'zipcode': current_user.zipcode
    }
    return render(request, 'users/index.html', context)

def signup(request):
    if 'loggedin_id' in request.session:
        messages.error(request, 'You are already signed up! Log out first to be able to sign up for a new account.')
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
        new_user.current_group.add(new_user)
        for food_id in request.POST.getlist('fav_food'):
            new_user.fav_foods.add(FoodCategory.objects.get(id=food_id))

        request.session['last_name'] = ''
        request.session['email'] = ''
        request.session['zipcode'] = ''
        request.session['term'] = ''
        request.session['fav_food'] = []
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
                request.session['term'] = ''
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

def profile(request):
    if 'loggedin_id' not in request.session:
        messages.error(request, 'Must be logged in to view')
        return redirect(reverse('users:signup'))
    current_user = User.objects.get(id=request.session['loggedin_id'])
    fav_foods = current_user.fav_foods.all()
    fav_foods_ids = []
    for food in fav_foods:
        fav_foods_ids.append(food.id)
    context = {
        'user': current_user,
        'fav_foods_ids': fav_foods_ids,
        'friends': current_user.friends.all().order_by("last_name")
    }
    return render(request, 'users/profile.html', context)

def update_profile(request):
    if request.method == 'POST':
        # FORM VALIDATION
        errors = User.objects.user_validator(request)
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect(reverse('users:profile'))

        # UPDATE USER'S DATABASE INFO
        pw_hashed = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
        current_user = User.objects.get(id=request.session['loggedin_id'])
        current_user.first_name = request.POST['first_name']
        current_user.last_name = request.POST['last_name']
        current_user.email = request.POST['email']
        current_user.zipcode = request.POST['zipcode']
        current_user.pw = pw_hashed

        fav_foods = current_user.fav_foods.all()
        for food in fav_foods:
            current_user.fav_foods.remove(food)
        for food_id in request.POST.getlist('fav_food'):
            current_user.fav_foods.add(FoodCategory.objects.get(id=food_id))
        current_user.save()
        return redirect(reverse('users:profile'))
    else:
        return redirect(reverse('users:index'))

def unfriend(request, id):
    if request.method == 'POST':
        current_user = User.objects.get(id=request.session['loggedin_id'])
        friend = User.objects.get(id=id)
        current_user.friends.remove(friend)
        friends = current_user.friends.all().order_by("last_name")
        return render(request, 'users/profile_displayfriends.html', {'friends': friends})
    else:
        return redirect(reverse('users:profile'))

def find_friend(request):
    if request.method == 'POST':
        current_user = User.objects.get(id=request.session['loggedin_id'])
        users = User.objects.filter(first_name__startswith=request.POST['find_friend_name']).exclude(id=current_user.id).exclude(friends__id=current_user.id).order_by("last_name")
        return render(request, 'users/findfriend.html', {'users': users})
    else:
        return redirect(reverse('users:index'))

def add_friend(request, id):
    if request.method == 'POST':
        current_user = User.objects.get(id=request.session['loggedin_id'])
        current_user.friends.add(User.objects.get(id=id))
        all_friends = current_user.friends.all()
        current_group = current_user.current_group.all().values('id')
        friends = all_friends.exclude(id__in=current_group).order_by("last_name")
        return render(request, 'users/displayfriends.html', {'friends': friends})
    else:
        return redirect(reverse('users:index'))

def display_friends(request):
    if request.method == 'POST':
        current_user = User.objects.get(id=request.session['loggedin_id'])
        all_friends = current_user.friends.all()
        current_group = current_user.current_group.all().values('id')
        print current_group
        friends = all_friends.exclude(id__in=current_group).order_by("last_name")
        return render(request, 'users/displayfriends.html', {'friends': friends})
    else:
        return redirect(reverse('users:index'))

def add_friend2group(request, id):
    if request.method == 'POST':
        current_user = User.objects.get(id=request.session['loggedin_id'])
        current_user.current_group.add(User.objects.get(id=id))
        members = current_user.current_group.all().exclude(id=current_user.id).order_by("last_name")
        return render(request, 'users/displaygroup.html', {'members': members})
    else:
        return redirect(reverse('users:index'))

def remove_friend_from_group(request, id):
    if request.method == 'POST':
        current_user = User.objects.get(id=request.session['loggedin_id'])
        friend = User.objects.get(id=id)
        current_user.current_group.remove(friend)
        members = current_user.current_group.all().exclude(id=current_user.id).order_by("last_name")
        return render(request, 'users/displaygroup.html', {'members': members})
    else:
        return redirect(reverse('users:index'))

def suggest_food(request):
    if 'loggedin_id' not in request.session:
        messages.error(request, 'Must be logged in to view')
        return redirect(reverse('users:signup'))
    current_user = User.objects.get(id=request.session['loggedin_id'])
    group = current_user.current_group.all()
    foods = {}
    for user in group:
        fav_foods = user.fav_foods.all()
        for food in fav_foods:
            if food.id in foods:
                foods[food.id] += 1
            else:
                foods[food.id] = 1
    food_suggestions = []
    for i in range(3):
        suggestion_id = max(foods, key=foods.get)
        food_suggestions.append(FoodCategory.objects.get(id=suggestion_id).category)
        del foods[suggestion_id]
    return HttpResponse(json.dumps(food_suggestions), content_type='application/json')
