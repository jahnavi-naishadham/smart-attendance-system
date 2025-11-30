# smart_attendance/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('attendance.urls')),
    path('', include('attendance.urls')),  # This includes the root URL
]
