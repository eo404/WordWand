from django.urls import path
from .views import ocr_test

urlpatterns = [
    path("ocr-test/", ocr_test),
]
