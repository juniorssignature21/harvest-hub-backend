from django import forms
from .models import Product, Category, UNIT_TYPE_CHOICES, AVAILABILITY_STATUS_CHOICES


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
class AddProductForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'e.g. Fresh Tomatoes'})
    )
    category = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        queryset=Category.objects.filter(is_active=True)
    )
    # Image uploads are handled separately in the view (multiple images),
    # so exclude the `image` field from the ModelForm to avoid FileField
    # validation errors when multiple files are uploaded.
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'Describe your product here...'})
    )
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'e.g. 10.99'})
    )
    unit_type = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        choices=UNIT_TYPE_CHOICES
    )
    availability_status = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        choices=AVAILABILITY_STATUS_CHOICES
    )
    stock_quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'e.g. 100'})
    )
    harvest_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'date'})
    )
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'date'})
    )
    farm_location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'e.g. Osisioma, Abia State'})
    )
    organic_certified = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'})
    )
    storage_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'Optional storage instructions...'})
    )
    usage_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'Optional usage instructions...'})
    )
    
    class Meta:
        model = Product
        fields = "__all__"
        exclude = ["created_at", "updated_at", "image", "sku"]
        