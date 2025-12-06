from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name="home"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<slug:slug>/', views.edit_product, name='edit_product'),
    path('delete-product/<slug:slug>/', views.delete_product, name='delete_product'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('view-products/', views.view_products, name="view_products"),
    
]