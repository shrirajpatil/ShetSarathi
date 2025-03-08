from django.urls import path
from . import views

app_name = 'openai_chatbot'
urlpatterns = [
    path('', views.chat, name='chat'),
]