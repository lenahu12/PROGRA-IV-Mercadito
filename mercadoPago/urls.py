from django.urls import path
from .views import CrearPreferenciaCarritoView, PagoExitosoView, PagoFallidoView, PagoPendienteView, NotificacionPagoView

urlpatterns = [
    path("carrito/pagar/", CrearPreferenciaCarritoView.as_view(), name="crear_preferencia_carrito"),
    path("pago-exitoso/", PagoExitosoView.as_view(), name="pago-exitoso"),
    path("pago-fallido/", PagoFallidoView.as_view(), name="pago-fallido"),
    path("pago-pendiente/", PagoPendienteView.as_view(), name="pago-pendiente"),
    path("notificacion-pago/", NotificacionPagoView.as_view(), name="notificacion-pago"),
]