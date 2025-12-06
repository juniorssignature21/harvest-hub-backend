from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import string
import random
import uuid

# Create your models here.
USER_TYPE = [
    ("farmer", "Farmer"),
    ("Buyer", "Buyer"),
    ("service_provider", "Service Provider"),
    ("admin", "Admin"),
]


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    token_created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username, _= self.email.split('@')
            username = CustomUser.objects.filter(username=self.username).exists()
            if username:
                suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
                self.username = f"{self.username}_{suffix}"
                
        super().save(*args, **kwargs)
        
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    state_of_origin = models.CharField(max_length=30, blank=True, null=True)
    nationality = models.CharField(max_length=30, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=30, blank=True, null=True)
    state_of_residence = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE, blank=True, null=True, default="buyer")
    slug = models.SlugField(unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.user.username}-profile"
            if Profile.objects.filter(slug=self.slug).exists():
                self.slug += '-' + str(random.randint(1000, 9999))
        super().save(*args, **kwargs)