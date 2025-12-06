from django.shortcuts import render, redirect
from userauths.decorators import email_verification_required
from django.conf import settings
import requests
from datetime import datetime

from .models import Farmer
from userauths.models import Profile
from .forms import FarmerRegisterForm

# Create your views here.


@email_verification_required
def dashboard(request):
    if request.user.profile.user_type != "farmer":
        return redirect('store:home')

    return render(request, 'farmers/dashboard.html')


@email_verification_required
def profile_settings(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    return render(request, "farmers/settings.html", {'profile': profile})

def farmer_edit_profile(request):
    user = request.user
    farmer = Farmer.objects.get(user=user)


def weather_view(request):
    
    # Determine city to query: use ?city= param, else try user's profile, else default
    city = request.GET.get('city')
    if not city and hasattr(request.user, 'profile'):
        # attempt to build a city/location string from profile fields
        prof = request.user.profile
        city = getattr(prof, 'state_of_residence', None) or getattr(prof, 'state_of_origin', None)

    if not city:
        city = 'Umuahia'

    # Open-Meteo does not require an API key. We'll attempt to geocode the city
    # using Open-Meteo's geocoding API and then call the forecast endpoint.
    context = {}
    try:
        geocode_url = 'https://geocoding-api.open-meteo.com/v1/search'
        gresp = requests.get(geocode_url, params={'name': city, 'count': 1}, timeout=5)
        gresp.raise_for_status()
        gdata = gresp.json()
        if gdata.get('results'):
            loc = gdata['results'][0]
            lat = loc['latitude']
            lon = loc['longitude']

            # Request forecast from Open-Meteo
            f_url = 'https://api.open-meteo.com/v1/forecast'
            params = {
                'latitude': lat,
                'longitude': lon,
                'current_weather': True,
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max',
                'timezone': 'auto'
            }
            fresp = requests.get(f_url, params=params, timeout=5)
            fresp.raise_for_status()
            fdata = fresp.json()

            def c_to_f(c):
                return round((c * 9/5) + 32)

            # current weather
            cur = fdata.get('current_weather', {})
            today = {
                'temp_f': c_to_f(cur.get('temperature', 0)),
                'humidity': None,
                'wind': round(cur.get('windspeed', 0)),
                'description': cur.get('weathercode', '')
            }

            # daily forecasts
            daily = fdata.get('daily', {})
            forecasts = []
            dates = daily.get('time', [])
            temps_max = daily.get('temperature_2m_max', [])
            temps_min = daily.get('temperature_2m_min', [])
            winds = daily.get('windspeed_10m_max', [])
            precs = daily.get('precipitation_sum', [])

            for i, d in enumerate(dates[:5]):
                temp_c = temps_max[i] if i < len(temps_max) else None
                forecasts.append({
                    'date': d,
                    'temp_f': c_to_f(temp_c) if temp_c is not None else None,
                    'humidity': None,
                    'wind': round(winds[i]) if i < len(winds) else None,
                    'description': 'N/A',
                })

            # rainfall series for chart (use precipitation_sum values)
            rainfall = [p for p in precs[:10]] if precs else []

            context['today'] = today
            context['forecasts'] = forecasts
            context['rainfall'] = rainfall
            context['city'] = city
        else:
            raise RuntimeError('Geocoding failed')
    except Exception:
        # fallback sample data
        context['today'] = {'temp_f': 78, 'humidity': 45, 'wind': 5, 'description': 'Sunny'}
        context['forecasts'] = [
            {'date': 'Tomorrow', 'temp_f': 72, 'humidity': 65, 'wind': 8, 'description': 'Cloudy'},
            {'date': 'Apr 27, 2025', 'temp_f': 68, 'humidity': 85, 'wind': 12, 'description': 'Rainy'},
            {'date': 'Apr 28, 2025', 'temp_f': 70, 'humidity': 75, 'wind': 10, 'description': 'Cloudy'},
            {'date': 'Apr 29, 2025', 'temp_f': 75, 'humidity': 50, 'wind': 7, 'description': 'Sunny'},
            {'date': 'Apr 30, 2025', 'temp_f': 77, 'humidity': 55, 'wind': 6, 'description': 'Partly Cloudy'},
        ]
        context['rainfall'] = [0, 3, 12, 5, 0]
        context['city'] = city

    # Additional analysis placeholders used in template
    context['impact'] = {'rainfall': 'Moderate impact expected.', 'humidity': 'Humidity may affect crop drying.'}
    context['irrigation'] = {'field': 'North Field', 'status': 'Optimal', 'soil_moisture': '48%'}

    return render(request, 'farmers/weather.html', context)