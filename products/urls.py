from django.urls import path
from .views import product_list, editar_producto, CrearProductoView, ProductDetailView, CarritoView, AñadirAlCarritoView, EliminarDelCarritoView, AñadirAlCarritoDesdeListaView, MisProductosView, EliminarProductoView, ActualizarCantidadView

urlpatterns = [
    path('', product_list, name='product_list'),         # /api/products/
    path("nuevo/", CrearProductoView.as_view(), name="crear-producto"), # /api/products/nuevo/esta utiliza Vista basada en Clase.
    path("editar/<int:pk>/", editar_producto, name="editar-producto"), # /api/products/editar
    path("<int:pk>/detalle/", ProductDetailView.as_view(), name="product_details"), #
    path("carrito/", CarritoView.as_view(), name="ver-carrito"), #
    path("añadir-al-carrito/<int:pk>/", AñadirAlCarritoView.as_view(), name="añadir-al-carrito"),
    path("añadir-al-carrito-desde-lista/<int:pk>/", AñadirAlCarritoDesdeListaView.as_view(), name="añadir-al-carrito-desde-lista"),
    path("eliminar-del-carrito/<int:pk>/", EliminarDelCarritoView.as_view(), name="eliminar-del-carrito"),
    path("mis-productos/", MisProductosView.as_view(), name="mis-productos"),
    path("eliminar-producto/<int:pk>/", EliminarProductoView.as_view(), name="eliminar-producto"),
    path("actualizar-cantidad/<int:pk>/", ActualizarCantidadView.as_view(), name="actualizar-cantidad"),

]