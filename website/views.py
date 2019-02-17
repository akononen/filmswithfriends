from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from website.models import *
from django.contrib.auth import login as auth_login #this is because the view also is named login
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
import json

def home(request):
    #return HttpResponse("home page")
    return render(request, "home.html")

def login(request):
    return render(request, "login.html")

def profile(request):
    return render(request, "profile.html")

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
