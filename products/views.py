
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DetailView
from django.views import View
from django.urls import reverse_lazy
from django.conf import settings
from .forms import ProductForm
from .models import Product


#Vista basada en clase.
class CrearProductoView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "crear_producto.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        # asigna el usuario logueado como dueño del producto
        form.instance.user = self.request.user
        return super().form_valid(form)
    
#Vista basada en clase.
class ProductDetailView(DetailView):
    model = Product
    template_name = "product_details.html"
    context_object_name = "product"

#Vista basada en clase del carrito.
class CarritoView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "carrito.html"
    context_object_name = "productos"

    #con esto redireccionamos al usuario luego de loguearse, al carrito de compras.
    login_url = settings.LOGIN_URL
    redirect_field_name = "next"

    def get_queryset(self):
        carrito = self.request.session.get("carrito", {})
        if isinstance(self.request.session.get("carrito"), list):
            self.request.session["carrito"] = {}
        product_ids = [int(pid) for pid in carrito.keys()]
        return Product.objects.filter(pk__in=product_ids)

#Petición POST para añadir productos al carrito:
class AñadirAlCarritoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Product, pk=pk)
        carrito = request.session.get("carrito", {})
        pk_str = str(pk)

        if pk_str in carrito:
            carrito[pk_str] += 1
        else:
            carrito[pk_str] = 1

        request.session["carrito"] = carrito
        return redirect("ver-carrito")

#Petición POST para añadir productos al carrito, específcamente desde la vista product_list.
class AñadirAlCarritoDesdeListaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Product, pk=pk)
        carrito = request.session.get("carrito", {})
        pk_str = str(pk)

        if pk_str in carrito:
            carrito[pk_str] += 1
            messages.info(request, f"🧠 {producto.nombre} ya estaba en el carrito. Se aumentó la cantidad.")
        else:
            carrito[pk_str] = 1
            messages.success(request, f"✅ {producto.nombre} fue añadido al carrito.")

        request.session["carrito"] = carrito
        return redirect("product_list")
    
#Peticion POST para eliminar los productos del carrito (todavía me cuesta llamar vista a una petición, preguntar al profesor si en peticiones POST se utiliza FBV O CBV)  
class EliminarDelCarritoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        carrito = request.session.get("carrito", {})
        pk_str = str(pk)

        if pk_str in carrito:
            del carrito[pk_str]
            request.session["carrito"] = carrito

        return redirect("ver-carrito")

#Vista para los productos del vendedor.
class MisProductosView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "user_products.html"
    context_object_name = "productos"

    login_url = "account_login"
    redirect_field_name = "next"

    def get_queryset(self):
        # solo los productos publicados por el usuario actual
        return Product.objects.filter(user=self.request.user)

#Vista para ELIMINAR un producto desde la vista del vendedor.
class EliminarProductoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Product, pk=pk, user=request.user)
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"🗑️ El producto '{nombre}' fue eliminado correctamente.")
        return redirect("mis-productos")  
    
#vista basada en función
@login_required #esta anotación la usamos en las vistas basadas en función, ya que en las de clase usamos el LoginRequiredMixin
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

class ActualizarCantidadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        producto = get_object_or_404(Product, pk=pk)
        try:
            cantidad = int(request.POST.get("cantidad", 1))
            if cantidad < 1 or cantidad > producto.stock:
                messages.warning(request, f"La cantidad debe estar entre 1 y {producto.stock}.")
            else:
                carrito = request.session.get("carrito", {})
                carrito[str(pk)] = cantidad
                request.session["carrito"] = carrito
                messages.success(request, f"Cantidad actualizada para '{producto.nombre}'.")
        except ValueError:
            messages.error(request, "Cantidad inválida.")
        return redirect("ver-carrito")
    



