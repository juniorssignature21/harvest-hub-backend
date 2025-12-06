from django.shortcuts import render, redirect
from userauths.forms import RegistrationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from userauths.models import Profile, CustomUser
from .utils import send_verification_email, send_welcome_email
from .decorators import email_verification_required


from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import uuid

# Create your views here.


def register_user(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create user but don't commit so we can set password properly
            user = form.save()
           
            # Ensure token and timestamp are set
            user.verification_token = uuid.uuid4()
            user.token_created_at = timezone.now()
            user.save()

            # Create profile
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            phone_number = form.cleaned_data.get('phone_number')

            Profile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number
            )

            # Send verification email
            try:
                send_verification_email(user, request)
                messages.success(request, 'Registration successful! Please check your email to verify your account.')
            except Exception as e:
                messages.warning(request, f'Account created but verification email failed to send. Error: {str(e)}')

            return redirect('userauths:signup-success')

    context = {'form': form}
    return render(request, 'userauths/register.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if email is verified
            if not user.email_verified:
                messages.error(request, 'Please verify your email before logging in. Check your inbox for the verification link.')
                return redirect('userauths:resend-verification')
            
            login(request, user)
            return redirect('store:home')  # Redirect to a success page.
        else:
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'userauths/login.html')

def verify_email_view(request, token):
    """
    Verify user's email using token
    """
    try:
        # Find user with token
        user = CustomUser.objects.get(verification_token=token)
        
        # Check if token is expired (24 hours)
        token_age = timezone.now() - user.token_created_at
        if token_age > timedelta(hours=24):
            messages.error(request, 'Verification link has expired. Please request a new one.')
            return redirect('userauths:resend-verification')
        
        # Verify email
        user.email_verified = True
        user.verification_token = uuid.uuid4()  # Generate new token for security
        user.token_created_at = timezone.now()
        user.save()
        
        # Send welcome email
        try:
            send_welcome_email(user)
        except:
            pass  # Welcome email failure shouldn't stop verification
        
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('userauths:login')
        
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('userauths:home')
    except Exception as e:
        messages.error(request, f'Verification failed: {str(e)}')
        return redirect('userauths:home')

def resend_verification_view(request):
    """
    Resend verification email
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            
            if user.email_verified:
                messages.info(request, 'Email is already verified.')
                return redirect('login')
            
            # Update token and send new email
            user.verification_token = uuid.uuid4()
            user.token_created_at = timezone.now()
            user.save()
            
            send_verification_email(user, request)
            messages.success(request, 'Verification email sent! Please check your inbox.')
            return redirect('login')
            
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    
    return render(request, 'registration/resend_verification.html')

def signup_success_view(request):
    """Success page after signup"""
    return render(request, 'registration/signup_success.html')

def logout_view(request):
    """Logout user"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('userauths:home')