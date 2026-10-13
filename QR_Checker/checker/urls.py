from django.urls import path
from . import views

urlpatterns = [
    path('', views.check, name='main'),
    path('checkin/', views.get_attendee, name='checkin'),
    path('checkin/<str:attendee_hash>', views.certificate, name='certificate'),
]
