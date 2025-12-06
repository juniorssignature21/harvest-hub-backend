from django.db import models
from django.utils.text import slugify
from userauths.models import CustomUser as User
from farmers.models import Farmer
import random

class Service_Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_provider_profile')
    company_name = models.CharField(max_length=100)
    company_address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        
        return self.company_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.company_name)
            if Service_Provider.objects.filter(slug=self.slug).exists():
                self.slug += '-' + str(random.randint(1000, 9999))
        super().save(*args, **kwargs)