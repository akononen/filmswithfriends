from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from website.models import *
from website.forms import RateMovieForm
from django.contrib.auth import login as auth_login #this is because the view also is named login
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import json

def home(request):
    #return HttpResponse("home page")
    if request.method == "POST":
        form = RateMovieForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.save()
            return HttpResponseRedirect('/home/')
    else:
        form = RateMovieForm()
    return render(request, "home.html", {"form":form})

def login(request):
    return render(request, "login.html")

def profile(request):
    profile_list = Profile.objects.exclude(user = request.user)
    user_list = []
    for profile in profile_list:
        user_list.append(profile.user)
    rated_movies = MovieRating.objects.filter(user=request.user)
    #should return also possible movies to watch with the person
    return render(request, "profile.html", {"user_list":user_list,
                                            "movies_list":rated_movies})
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

def remove_rating(request, movie_rating_id):
    movie_rating = MovieRating.objects.get(id=movie_rating_id)
    movie_rating.delete()
    return HttpResponseRedirect("/profile/")

# adding a friend to one-to-one link and to connections
#def add_friend(user, friend):
#    c1 = Connection(user1=user, user2=friend)
#    c2.save()
#def profile(request):
#    if request.method == "POST":
#        form = AddFriendForm(request.POST)
#        if form.is_valid():
#            new_friend = form.cleaned_data.get("friend_username")
#            user = request.user
#            friend = User.objects.get(username=friend)
#            add_friend(user, friend)
#            return HttpResponseRedirect('/profile/')
#
#    else:
#        form = AddFriendForm()
#
#    #list of user objects
#    friends_list = request.user.profile.friends.all()
#    return render(request, "profile.html", {'form':form,
#                                            'friend_list':friends_list})
