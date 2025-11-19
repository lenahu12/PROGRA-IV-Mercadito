from rest_framework import viewsets
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import ProductForm
from .models import Product
from .serializers import ProductSerializer



#Vista basada en clase
class CrearProductoView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "crear_producto.html"
    success_url = reverse_lazy("product-list")

    def form_valid(self, form):
        # asigna el usuario logueado como dueño del producto
        form.instance.user = self.request.user
        return super().form_valid(form)

#vista basada en función
@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Product, pk=pk)

    if producto.user != request.user:
        messages.error(request, "No tenés permiso para editar este producto.")
        return redirect('/api/products/')

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect('/api/products/')
    else:
        form = ProductForm(instance=producto)

    return render(request, "editar_producto.html", {"form": form, "producto": producto})

def product_list(request):
    productos = Product.objects.all()
    return render(request, 'product_list.html', {'productos': productos})