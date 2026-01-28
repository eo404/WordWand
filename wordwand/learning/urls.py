from django.urls import path
from . import views

urlpatterns = [
    path("home/",  views.home, name="home"),
    path("letters/", views.letters_intro, name="letters_intro"),
    path("alphabetgrid/", views.alphabetgrid, name="alphabetgrid"),
]
