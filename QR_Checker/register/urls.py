from django.urls import path
from . import views

urlpatterns = [
    path('', views.post, name='main'),
    path('register/new', views.post_new, name='post_new'),
]
