from django.urls import path
from . import views

urlpatterns = [
    path('' , views.home , name='home'),
    path('scan/', views.hand_scan_view, name='hand_scan'),
]