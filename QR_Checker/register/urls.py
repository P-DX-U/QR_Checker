from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_register, name='post_register')
]
