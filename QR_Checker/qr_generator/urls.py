from django.urls import path
from . import views

urlpatterns = [
    path('attendees/', views.attendees_list, name='attendees_list'),
    path('delete_register/<str:attendee_hash>/', views.delete_register, name='delete_register'),
    path('create_qr/<str:attendee_hash>/', views.create_qr, name='create_qr'),
]