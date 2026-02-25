from django.urls import path
from . import views

urlpatterns = [
    path("home/",  views.home, name="home"),
    path("letters/", views.letters_intro, name="letters_intro"),
    path("alphabetgrid/", views.alphabetgrid, name="alphabetgrid"),
    path('letter/<str:letter>/', views.letter, name='letter'),
    path('letter/<str:letter>/video/', views.letter_video, name='letter_video'),
    path("letter/<str:letter>/trace/", views.letter_trace, name="letter_trace"),
]
