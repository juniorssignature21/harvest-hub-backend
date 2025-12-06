from django.db import models
import random

# Create your models here.
class Farmer(models.Model):
    user = models.OneToOneField('userauths.CustomUser', on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=100)
    farm_location = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.farm_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.farm_name.lower().replace(' ', '-')  # Simple slug generation
            if Farmer.objects.filter(slug=self.slug).exists():
                self.slug += '-' + str(random.randint(1000, 9999))
        super().save(*args, **kwargs)
        


        

