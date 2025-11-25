from django.http import HttpResponse
from django.views import View
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .utils import render_to_pdf  # tu función que convierte HTML a PDF

class TestEmailView(View):
    def get(self, request):
        try:
            # 1. Enviar correo simple de prueba
            send_mail(
                subject="Prueba de correo desde Django",
                message="Este es un correo de prueba para validar el backend SMTP.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["nahuelquintana997@gmail.com"],
                fail_silently=False,
            )

            # 2. Generar PDF de prueba
            context = {
                "cliente": "testuser@comprador.com",
                "fecha": "25/11/2025",
                "items": [
                    {"nombre": "Producto demo", "cantidad": 1, "precio": 100, "subtotal": 100},
                ],
                "total": 100,
            }
            pdf = render_to_pdf("quote.html", context)

            if pdf:
                # Guardar localmente
                with open("presupuesto_test.pdf", "wb") as f:
                    f.write(pdf)
                print("📄 PDF guardado como presupuesto_test.pdf")

                # Enviar PDF por correo
                email = EmailMessage(
                    "Presupuesto de prueba",
                    "Adjunto encontrarás el presupuesto en PDF.",
                    settings.DEFAULT_FROM_EMAIL,
                    ["nahuelquintana997@gmail.com"],
                )
                email.attach("presupuesto.pdf", pdf, "application/pdf")
                email.send()

            return HttpResponse("✅ Correo y PDF de prueba enviados/guardados correctamente")

        except Exception as e:
            return HttpResponse(f"❌ Error al enviar el correo: {e}")
