from django.shortcuts import render, redirect, HttpResponse

def index(request):
    return render(request, 'users/index.html')

def register(request):
    return render(request, 'users/register.html')