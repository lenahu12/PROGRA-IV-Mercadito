from .models import Compra, DetalleCompra
from users.models import CustomUser
from django.core.mail import EmailMessage
from django.conf import settings
from .utils import render_to_pdf

def enviar_presupuesto_por_pago(payment_data):
    # Extraer el ID del comprador desde external_reference
    referencia = payment_data.get("external_reference")
    try:
        comprador = CustomUser.objects.get(id=referencia)
    except CustomUser.DoesNotExist:
        print("❌ Comprador no encontrado por referencia externa")
        comprador = CustomUser(email="nahuelquintana997@gmail.com") 

    # Buscar la última compra del usuario (la más reciente)
    compra = Compra.objects.filter(comprador=comprador).order_by("-fecha").first()
    if not compra:
        print("❌ No se encontró ninguna compra para este usuario")
        return

    detalles = DetalleCompra.objects.filter(compra=compra)

    items = []
    for detalle in detalles:
        items.append({
            "nombre": detalle.producto.nombre,
            "cantidad": detalle.cantidad,
            "precio": detalle.precio_unitario,
            "subtotal": detalle.subtotal(),
        })

    context = {
        "cliente": comprador.email,
        "fecha": compra.fecha.strftime("%d/%m/%Y"),
        "items": items,
        "total": compra.total,
    }

    pdf = render_to_pdf("quote.html", context)
    print("🧩 Contexto para PDF:", context)
    if pdf:
        print("✅ PDF renderizado correctamente, procediendo a enviar email")
        email = EmailMessage(
            "Presupuesto de tu compra",
            "Adjunto encontrarás el presupuesto en PDF.",
            settings.DEFAULT_FROM_EMAIL,
            [comprador.email],
        )
        email.attach("presupuesto.pdf", pdf, "application/pdf")
        email.send(fail_silently=False)
    else:
        print("❌ No se pudo renderizar el PDF")
