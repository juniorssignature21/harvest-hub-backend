from django.urls import path
from . import views

app_name = 'userauths'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_user, name='register'),
    path('signup-success/', views.signup_success_view, name='signup-success'),
    path('verify/<uuid:token>/', views.verify_email_view, name='verify-email'),
    path('resend-verification/', views.resend_verification_view, name='resend-verification'),
    # path('profile/', views.profile_view, name='profile'),
]