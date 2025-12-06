from django.urls import path
from . import views

app_name = 'farmers'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile-settings/', views.profile_settings, name='settings'),
    path('weather/', views.weather_view, name='weather'),
]

