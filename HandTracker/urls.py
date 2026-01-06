from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.hand_scan_view, name='hand_scan'),
]