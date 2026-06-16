from django.urls import path
from . import views

urlpatterns = [
    path('attendees/', views.attendees_list, name='attendees_list'),
]