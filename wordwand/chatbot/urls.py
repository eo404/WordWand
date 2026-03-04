from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/',         views.chatbot,         name='chatbot'),
    path('chatbot/message/', views.chatbot_message, name='chatbot_message'),
]
