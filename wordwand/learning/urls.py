from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("letters/", views.letters_intro, name="letters_intro"),
    path("letters/grid/", views.alphabetgrid, name="alphabetgrid"),
    path("letters/<str:letter>/", views.letter, name="letter"),
    path("letters/<str:letter>/video/", views.letter_video, name="letter_video"),
    path("letters/<str:letter>/trace/", views.letter_trace, name="letter_trace"),
]
