from django.shortcuts import render, redirect, HttpResponse

def index(request):
    return render(request, 'users/index.html')

def signup(request):
    return render(request, 'users/signup.html')

def process_signup(request):
    if request.method == "POST":
        print len(request.POST.getlist('fav_food'))
        return render(request, 'users/home.html')