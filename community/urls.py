from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('add/', views.add_post, name='add_post'),
]