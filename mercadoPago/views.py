import mercadopago
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from compra.models import Compra, DetalleCompra, CarritoTemporal
from django.conf import settings
import mercadopago
from products.models import Product
from users.models import CustomUser
from compra.models import Compra, DetalleCompra, CarritoTemporal
from compra.tasks import enviar_presupuesto_por_pago
#Vista para mercado pago
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
                "success": f"{base_url}/api/pagos/pago-exitoso/",
                "failure": f"{base_url}/api/pagos/pago-fallido/",
                "pending": f"{base_url}/api/pagos/pago-pendiente/",
            },
            "auto_return": "approved",
            "notification_url": f"{base_url}/api/pagos/notificacion-pago/",
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