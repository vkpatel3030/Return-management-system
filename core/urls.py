from django.urls import path , include
from . import views

urlpatterns = [
    path('', include('auth_google.urls')),
    path('', views.home, name='home'),  
    path('upload/', views.upload_file, name='upload_file'),
    path('scan/', views.scan_awb, name='scan_awb'),
    path('save-scan/', views.save_scan, name='save_scan'),
    path('compare/', views.compare_data, name='compare'),
    path('download-matched/', views.download_matched, name='download_matched'),
    path('download-unmatched/', views.download_unmatched, name='download_unmatched'),

]
