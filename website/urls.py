from django.urls import path
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("home/", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("profile/remove_rating/<int:movie_rating_id>", views.remove_rating, name="remove_rating"),
    path("profile/change_rating/<int:movie_rating_id>/<int:new_rating>", views.change_rating, name="change_rating"),
    path("ratemovie/<slug:imdb_id>/<int:rating>", views.rate_movie, name="rate_movie"),
    path("recommendations/<int:other_user_id>", views.recommendations, name="recommendations"),
    path("profile/dashboard", views.dashboard, name = "dashboard"),
    path("makedb/", views.makedb, name="makedb"),

]
