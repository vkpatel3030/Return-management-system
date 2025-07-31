
from django.urls import path
from . import views

urlpatterns = [
    path('google/login/', views.google_login, name='google_login'),
    path('google/redirect/', views.google_redirect, name='google_redirect'),
    path('drive/', views.drive_list, name='drive_list'),
]
