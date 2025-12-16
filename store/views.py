from django.shortcuts import render, redirect
from django.contrib import messages

from userauths.decorators import email_verification_required
from .forms import AddProductForm
from . import models as store_models
from farmers.models import Farmer

from service_providers.models import Service_Provider


# Create your views here.
def custom_404_view(request, exception):
    return render(request, 'store/404.html', status=404)

def custom_500_view(request):
    return render(request, 'store/500.html', status=500)

# @email_verification_required
def home(request):
    categories = store_models.Category.objects.all()
    products = store_models.Product.objects.filter(availability_status='in_stock')
    context = {
        "categories": categories,
        "products":products
    }
    return render(request, 'store/marketplace.html', context)

@email_verification_required
def index(request):
    if request.user.profile.user_type == "farmer":
        return redirect('farmers:dashboard')
    elif request.user.profile.user_type == "buyer":
        return redirect("store:buyer_dashboard")
    elif request.user.profile.user_type == "service_provider":
        return render(request, 'store/service_provider_dashboard.html')
    elif request.user.profile.user_type == "admin":
        return render(request, 'store/admin_dashboard.html')
    else:
        return render(request, 'store/dashboard.html')

@email_verification_required
def buyer_dashoard(request):
    user = request.user
    return render(request, "store/dashboard.html")


def orders(request):
    return render(request, "store/myorder.html")




@email_verification_required
def add_product(request):
    form = AddProductForm()
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Save product instance first, then handle multiple uploaded images
            if request.user.profile.user_type == "farmer":
                farm = Farmer.objects.get(user=request.user)   
                product = form.save(commit=False)
                product.farm = farm
                product.save()  
            elif request.user.profile.user_type == "service_provider":
                owner = Service_Provider.objects.get(user=request.user)
                product = form.save(commit=False)
                product.service_provider = owner
                product.save()
            else:
                product = form.save(commit=False)
                product.save()
            # handle multiple uploaded images from the 'image' input
            images = request.FILES.getlist('image')
            for idx, img in enumerate(images):
                store_models.ProductImage.objects.create(product=product, image=img, order=idx)

            messages.success(request, "Successfully Added Product")
            return redirect("store:dashboard")
        else:
            error_messages = {
            field: ', '.join(str(e.message) for e in error_list)
            for field, error_list in form.errors.as_data().items()
            }
            
            for field, error_message in error_messages.items():
                messages.error(request, f"{field}: {error_message}")
                
    context = {
        "form": form
    }
    
    return render(request, "farmers/addproduct.html", context)

@email_verification_required
def edit_product(request, slug):
    product = store_models.Product.objects.get(slug=slug)
    form = AddProductForm(instance=product)
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()

            # If new images uploaded, add them
            images = request.FILES.getlist('image')
            for idx, img in enumerate(images):
                store_models.ProductImage.objects.create(product=product, image=img, order=idx)

            messages.success(request, "Successfully Updated Product")
            return redirect("store:dashboard")
        else:
            error_messages = {
            field: ', '.join(str(e.message) for e in error_list)
            for field, error_list in form.errors.as_data().items()
            }
            
            for field, error_message in error_messages.items():
                messages.error(request, f"{field}: {error_message}")
                
    context = {
        "form": form,
        "product": product
    }
    
    return render(request, "store/edit_product.html", context)

@email_verification_required
def product_detail(request, slug):
    
    product = store_models.Product.objects.get(slug=slug)
    context = {
        "product": product
    }
    return render(request, "farmers/viewsub.html", context)

@email_verification_required
def delete_product(request, slug):
    product = store_models.Product.objects.get(slug=slug)
    product.delete()
    messages.success(request, "Successfully Deleted Product")
    return redirect("store:dashboard")

@email_verification_required
def view_products(request):
    farmer = Farmer.objects.get(user=request.user)
    products = store_models.Product.objects.filter(farm=farmer)
    context = {
        "farmer":farmer,
        "products":products
    }
    return render(request, "farmers/viewproducts.html", context)

@email_verification_required
def profile_settings(request):
    user = request.user
    return render(request, "store/settings.html")
