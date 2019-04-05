from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from website.models import *
from website.forms import RateMovieForm
from website.utils import *
from django.contrib.auth import login as auth_login #this is because the view also is named login
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from django.db.models import Q
import json
import sys
#"s3", "postgres://testi:saatana@localhost/imdbraw"
from imdb import IMDb

def makedb(request):
    ia = IMDb("s3", "postgres://testi:saatana@localhost/imdbraw", adultSearch=False)
    #Indexes in database: 1-103045 --> next we will loop backwards
    #the right amount: 9916896
    movies_count = 9916896
    i = 9916896
    while i != 103046:
        index = str(i).zfill(7)
        print(index)
        success_counter = 1
        fail_counter = 1

        #try:
        movie = ia.get_movie(index)
        try:
            kind = movie["kind"]
        except KeyError:
            kind = ""

        if kind == "movie":

            try:
                genre1 = movie["genre"][0]
            except KeyError:
                genre1 = ""
            try:
                genre2 = movie["genre"][1]
            except (KeyError, IndexError):
                genre2 = ""
            try:
                genre3 = movie["genre"][2]
            except (KeyError, IndexError):
                genre3  = ""
            try:
                director = movie["director"][0]["name"]
                director_id = movie["director"][0].personID
            except KeyError:
                director = ""
                director_id = ""
            try:
                writer = movie["writer"][0]["name"]
                writer_id = movie["writer"][0].personID
            except KeyError:
                writer = ""
                writer_id = ""
            try:
                actor1 = movie["cast"][0]["name"]
                actor1_id = movie["cast"][0].personID
            except KeyError:
                actor1 = ""
                actor1_id = ""
            try:
                actor2 = movie["cast"][1]["name"]
                actor2_id = movie["cast"][1].personID
            except (KeyError, IndexError):
                actor2=""
                actor2_id=""
            try:
                actor3 = movie["cast"][2]["name"]
                actor3_id = movie["cast"][2].personID
            except (KeyError, IndexError):
                actor3 = ""
                actor3_id = ""

            #try:
            movie_object = Movie(imdb_movie_id = movie.movieID,
                                title = movie["title"],
                                director = director,
                                director_id = director_id,
                                writer = writer,
                                writer_id = writer_id,
                                actor1 = actor1,
                                actor1_id = actor1_id,
                                actor2 = actor2,
                                actor2_id = actor2_id,
                                actor3 = actor3,
                                actor3_id = actor3_id,
                                genre1 = genre1,
                                genre2 = genre2,
                                genre3 = genre3)

            movie_object.save()
            success_counter += 1
        else:
            fail_counter += 1

        #fail_counter =+ 1

        print("Process: ", success_counter+fail_counter/movies_count-103045)
        #print("Fails: ", fail_counter, "   Sucessess: ", success_counter)
        #print("Fail%: ", fail_counter/(fail_counter+success_counter), "   Success%: ", success_counter/(fail_counter+success_counter))
        i -= 1

    return HttpResponseRedirect("/profile/")


def home(request):
    #return HttpResponse("home page")
    if request.method == "POST":
        form = RateMovieForm(request.POST)
        if form.is_valid():

            title = form.cleaned_data.get('title')
            rating = form.cleaned_data.get('rating')

            ia = IMDb()
            movies = ia.search_movie(title)
            suggestions_title = []
            suggestions_year = []
            movie_ids = []
            for movie in movies:
                #check if the movie has already been rated by the user
                #if not, the movie is added to the list
                if movie["kind"] is "movie":
                    try:
                        MovieRating.objects.get(user = request.user, imdb_movie_id = movie.movieID)
                    except ObjectDoesNotExist:
                        #trying to access "year" sometimes fails, if so year=0000
                        try:
                            suggestions_year.append(movie["year"])
                        except:
                            suggestions_year.append(0000)
                        suggestions_title.append(movie["title"])
                        movie_ids.append(movie.movieID)
            suggestions = zip(suggestions_title, suggestions_year, movie_ids)
            return render(request, "specify.html", {"title":title,
                                                    "rating":rating,
                                                    "suggestions": suggestions})

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

def change_rating(request, movie_rating_id, new_rating):
    movie_rating = MovieRating.objects.get(id=movie_rating_id)
    movie_rating.rating = new_rating
    movie_rating.save()
    return HttpResponseRedirect("/profile/")

def rate_movie(request, imdb_id, rating):
    ia = IMDb()
    return_message= ""
    movie = ia.get_movie(imdb_id)
    try:
        mrating = MovieRating(user = request.user, imdb_movie_id=imdb_id,
                                title = movie["title"], rating=rating)
        mrating.save()
        for director in movie["director"]:
            drating = DirectorRating(user=request.user, director = director["name"],
                                        imdb_person_id = director.personID, rating = rating)
            drating.save()
        for writer in movie["writer"]:
            wrating = WriterRating(user=request.user, writer = writer["name"],
                                    imdb_person_id = writer.personID, rating = rating)
            wrating.save()
        #six main actors are  taken into account in actor raitings.
        for index in range(6):
            actor = movie["cast"][index]
            arating = ActorRating(user=request.user, actor = actor["name"],
                                    imdb_person_id=actor.personID, rating=rating)
            arating.save()

        for genre in movie["genres"]:
            grating = GenreRating(user=request.user, genre = genre, rating = rating)

            grating.save()

    except:
        pass

    #return to home page
    return HttpResponseRedirect("/home/")

def recommendations(request, other_user_id):

    #Collecting both users ratings from all models
    user_gavgs = GenreRating.objects.filter(user = request.user).values("genre").annotate(Avg("rating")).order_by("-rating__avg")
    user_wavgs = WriterRating.objects.filter(user = request.user).values("writer").annotate(Avg("rating")).order_by("-rating__avg")
    user_davgs = DirectorRating.objects.filter(user = request.user).values("director").annotate(Avg("rating")).order_by("-rating__avg")
    user_aavgs = ActorRating.objects.filter(user = request.user).values("actor").annotate(Avg("rating")).order_by("-rating__avg")

    other_user_gavgs = GenreRating.objects.filter(user = other_user_id).values("genre").annotate(Avg("rating")).order_by("-rating__avg")
    other_user_wavgs = WriterRating.objects.filter(user = other_user_id).values("writer").annotate(Avg("rating")).order_by("-rating__avg")
    other_user_davgs = DirectorRating.objects.filter(user = other_user_id).values("director").annotate(Avg("rating")).order_by("-rating__avg")
    other_user_aavgs = ActorRating.objects.filter(user = other_user_id).values("actor").annotate(Avg("rating")).order_by("-rating__avg")

    #finding first common genre from both users --> this is the genre that is
    #used fot searching suggested movies
    genre = get_first_common(user_gavgs, other_user_gavgs, "genre").lower()
    director = get_first_common(user_davgs, other_user_davgs, "director")
    actor = get_first_common(user_aavgs, other_user_aavgs, "actor")
    writer = get_first_common(user_wavgs, other_user_wavgs, "writer")

    directors = get_commons(user_davgs, other_user_davgs, "director")
    writers = get_commons(user_wavgs, other_user_wavgs, "writer")

    #keywords = get_keywords(genre)
    #movies = get_movies(keywords)
    print(director)
    print(writer)
    print(genre)

    all_movies =Movie.objects.filter(Q(genre1=genre)|Q(genre2=genre)|Q(genre3=genre))

    common_director1 = all_movies.filter(director=directors[0])
    try:
        common_director2 = all_movies.filter(director=directors[1])
    except IndexError:
        common_director2 = Movie.objects.none()
    try:
        common_director3 = all_movies.filter(director=directors[2])
    except IndexError:
        common_director3 = Movie.objects.none()
    common_writer1 = all_movies.filter(writer = writers[0])
    try:
        common_writer2 = all_movies.filter(writer = writers[1])
    except IndexError:
        common_writer2 = Movie.objects.none()
    try:
        common_writer3 = all_movies.filter(writer = writers[2])
    except IndexError:
        common_writer3 = Movie.objects.none()
    for i in common_director1:
        print(i.title)
    for i in common_writer1:
        print(i.title)
    suggestions  = common_director1.union(common_director2, common_director3, common_writer1, common_writer2, common_writer3)
    for i in suggestions:
        print(i.title)
    #taking out movies that either one has rated
    rated_movies = MovieRating.objects.filter(Q(user = request.user)|Q(user=other_user_id))
    rated_ids = []
    movies = []
    m_year = []
    m_director = []
    m_writer = []
    #ia = IMDb()
    for rm in rated_movies:
        rated_ids.append(rm.imdb_movie_id)
    print("append")
    for movie in suggestions:
        if movie.imdb_movie_id not in rated_ids:
            movies.append(movie.title)
            # m = ia.get_movie(movie.imdb_movie_id)
            # # try:
            # #     m_year.append(m["year"])
            # # except KeyError:
            # #     m_year.append(0)
            m_director.append(movie.director)
            m_writer.append(movie.writer)
            print(movie.title)
            print(movie.director)
            print(movie.writer)
    suggestions = zip(movies, m_director, m_writer)
    #for i in suggestions:
        #print(i)
    return render(request, "recommendations.html", {"suggestions":suggestions})
