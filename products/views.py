import mercadopago
from rest_framework import viewsets
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, DetailView
from django.views import View
from django.urls import reverse_lazy
from django.conf import settings
from orders.models import Compra, DetalleCompra, CarritoTemporal
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
    
#Vista para mercado pago:
class CrearPreferenciaCarritoView(View):
    def get(self, request):
        carrito = request.session.get("carrito", {})
        base_url = request.build_absolute_uri("/").replace("http://", "https://").rstrip("/")
        print("🔵 URL de éxito:", base_url + "/pago-exitoso/")
        print("🔴 URL de fallo:", base_url + "/pago-fallido/")
        print("🟡 URL de pendiente:", base_url + "/pago-pendiente/")
        print("🛒 Carrito recibido:", carrito)

        if not carrito:
            return JsonResponse({
                "error": "El carrito está vacío.",
            }, status=400)

        # ✅ Guardar el carrito en la base
        CarritoTemporal.objects.create(usuario=request.user, contenido=carrito)
        print("📦 Carrito persistido en CarritoTemporal")

        product_ids = [int(pid) for pid in carrito.keys()]
        productos = Product.objects.filter(id__in=product_ids)

        items = []
        for producto in productos:
            cantidad = int(carrito.get(str(producto.id), 1))
            items.append({
                "title": producto.nombre,
                "quantity": cantidad,
                "unit_price": float(producto.precio),
                "currency_id": "ARS",
            })

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        preference_data = {
            "items": items,
            "back_urls": {
                "success": f"{base_url}/api/products/pago-exitoso/",
                "failure": f"{base_url}/api/products/pago-fallido/",
                "pending": f"{base_url}/api/products/pago-pendiente/",
            },
            "auto_return": "approved",
            "notification_url": f"{base_url}/api/products/notificacion-pago/",
            "external_reference": str(request.user.id),
        }

        preference = sdk.preference().create(preference_data)
        print("🧾 Preferencia generada:", preference)

        init_point = preference.get("response", {}).get("init_point")
        if not init_point:
            return JsonResponse({
                "error": "No se pudo crear la preferencia de pago.",
            }, status=500)

        return JsonResponse({"init_point": init_point})

class PagoExitosoView(View):
    template_name = "pago_exitoso.html"

    def get(self, request):
        print("✅ Entrando a PagoExitosoView")
        print("🔷 Parámetros recibidos:", request.GET.dict())
        payment_id = request.GET.get("payment_id")
        status = request.GET.get("status")

        contexto = {
            "estado": "desconocido",
            "mensaje": "No se pudo verificar el estado del pago.",
            "comprador": None,
            "monto": None,
        }

        if payment_id and status == "approved":
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            pago = sdk.payment().get(payment_id)
            datos = pago.get("response", {})

            contexto["estado"] = datos.get("status", "sin estado")
            contexto["mensaje"] = "✅ ¡Pago aprobado correctamente!"
            contexto["comprador"] = datos.get("payer", {}).get("email", "Desconocido")
            contexto["monto"] = datos.get("transaction_amount", 0)

            #se limpia el carrito
            if "carrito" in request.session:
                del request.session["carrito"]
                request.session.modified = True
                print("🧹 Carrito eliminado de la sesión")

        return render(request, self.template_name, contexto)


class PagoFallidoView(View):
    template_name = "pago_fallido.html"

    def get(self, request):
        # Parámetros que Mercado Pago envía en la redirección
        payment_id = request.GET.get("payment_id")
        status = request.GET.get("status")

        contexto = {
            "mensaje": "❌ El pago no pudo completarse.",
            "estado": status or "fallido",
            "payment_id": payment_id,
        }

        return render(request, self.template_name, contexto)

class PagoPendienteView(View):
    template_name = "pago_pendiente.html"

    def get(self, request):
        payment_id = request.GET.get("payment_id")
        status = request.GET.get("status")

        contexto = {
            "mensaje": "⏳ Tu pago está pendiente de confirmación.",
            "estado": status or "pendiente",
            "payment_id": payment_id,
        }

        return render(request, self.template_name, contexto)

    
@method_decorator(csrf_exempt, name='dispatch')
class NotificacionPagoView(View):
    def post(self, request):
        from users.models import CustomUser
        from orders.models import Compra, DetalleCompra
        from products.models import Product
        from quotes.tasks import enviar_presupuesto_por_pago
        import mercadopago

        payment_id = request.GET.get("id")
        topic = request.GET.get("topic")

        if topic == "payment" and payment_id:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment = sdk.payment().get(payment_id)
            estado = payment["response"]["status"]
            print(f"⚡ Webhook recibido: pago {payment_id} con estado {estado}")

            if estado == "approved":
                try:
                    user_id = int(payment["response"]["external_reference"])
                    comprador = CustomUser.objects.get(id=user_id)
                except (ValueError, CustomUser.DoesNotExist):
                    print("❌ Comprador no encontrado")
                    return HttpResponse("Comprador no registrado", status=404)

                carrito_temp = CarritoTemporal.objects.filter(usuario=comprador).order_by("-creado").first()
                carrito = carrito_temp.contenido if carrito_temp else {}
                compra = Compra.objects.create(comprador=comprador, total=0)
                total = 0

                for producto_id, cantidad in carrito.items():
                    try:
                        producto = Product.objects.get(id=producto_id)
                        subtotal = producto.precio * cantidad
                        DetalleCompra.objects.create(
                            compra=compra,
                            producto=producto,
                            cantidad=cantidad,
                            precio_unitario=producto.precio
                        )
                        producto = Product.objects.get(id=producto_id)
                        producto.stock -= cantidad
                        producto.save()
                        print(f"📉 Stock actualizado: {producto.nombre} → {producto.stock}")
                        total += subtotal
                    except Product.DoesNotExist:
                        print(f"⚠️ Producto con ID {producto_id} no encontrado")

                compra.total = total
                compra.save()
                if carrito_temp:
                    carrito_temp.delete()
                    print("🗑️ Carrito temporal eliminado")
                enviar_presupuesto_por_pago(payment["response"])
                print(f"✅ Compra #{compra.id} registrada para {comprador.email}")

        return HttpResponse("OK")


