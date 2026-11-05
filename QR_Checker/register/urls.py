from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.post, name='main'),
    path('register/new', views.post_new, name='post_new'),
    path('register/bulk', views.post_bulk_upload, name='post_bulk_upload'),
    path('register/bulk/review', views.post_bulk_review, name='post_bulk_review'),
    path('register/bulk/cancel', views.post_bulk_cancel, name='post_bulk_cancel'),
    path('register/bulk/template.csv', views.post_bulk_template, name='post_bulk_template'),
]
