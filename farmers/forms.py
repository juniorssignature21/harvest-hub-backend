from django import forms
from .models import Farmer

class FarmerRegisterForm(models.Model):
    class Meta:
        model = Farmer
        fields = ...
