from django.shortcuts import render
from products.models import Product

def home_view(request):
    productos = Product.objects.order_by('-creado_en')[:5] 
    return render(request, 'home.html', {'productos': productos})