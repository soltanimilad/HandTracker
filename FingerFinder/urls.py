from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tracker/', include('HandTracker.urls')), # This makes the page live at /tracker/scan/
]