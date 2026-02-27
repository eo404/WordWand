from django.urls import path
from . import views

urlpatterns = [
    path("reader/", views.reader, name="reader"),
]
