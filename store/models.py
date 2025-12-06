from django.db import models    
from django.utils.text import slugify
from userauths.models import CustomUser as User
from farmers.models import Farmer
import uuid
UNIT_TYPE_CHOICES = [
    ('kg', 'Kilogram'),
    ('lb', 'Pound'),
    ('piece', 'Piece'),
    ('liter', 'Liter'),
    ('pack', 'Pack'),
    ('bag_50kg', 'Bag 50kg'),
    ('bag_100kg', 'Bag 100kg'),
    ('crate', 'Crate'),
    ('bunch', 'Bunch'),
    ('ton', 'Ton'),
]

AVAILABILITY_STATUS_CHOICES = [
    ('in_stock', 'In Stock'),
    ('out_of_stock', 'Out of Stock'),
    ('pre_order', 'Pre-order'),
    ('discontinued', 'Discontinued'),
]
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name




class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]
    
    farm = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    service_provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provided_products', null=True, blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    
    image = models.FileField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_type = models.CharField(max_length=50, blank=True, null=True)
    
    availability_status = models.CharField(max_length=50, default='in_stock', choices=AVAILABILITY_STATUS_CHOICES)
    sku = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    stock_quantity = models.IntegerField(default=0)
    
    harvest_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    farm_location = models.CharField(max_length=200, blank=True, null=True)
    organic_certified = models.BooleanField(default=False, help_text="Indicates if the product is organically certified") 
   
    storage_instructions = models.TextField(blank=True, null=True)
    usage_instructions = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    def __str__(self):
        return self.name
    
    def product_images(self):
        return ProductImage.objects.filter(product=self).order_by('order')

    def primary_image(self):
        primary = ProductImage.objects.filter(product=self, is_primary=True).first()
        if primary:
            return primary
        return ProductImage.objects.filter(product=self).order_by('order').first()
    def count_sold(self):
        # Placeholder method; actual implementation would depend on Order models
        return 0
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-is_primary']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"



class ProductVariant(models.Model):
    """For products with variations like size, color, etc."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100, help_text="e.g., 'Small Red', 'Large Blue'")
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    
    # Variant attributes
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"

