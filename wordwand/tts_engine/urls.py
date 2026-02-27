from django.urls import path
from .views import reader

urlpatterns = [
    path("reader/", reader, name="reader"),
]
