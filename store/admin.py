from django.contrib import admin
from store.models import (
    Product,
    Category,
    ProductImage
)
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ["name", "slug", "service_provider", "category", "farm_location"]

admin.site.register(Product, ProductAdmin)

admin.site.register(Category)
admin.site.register(ProductImage)
