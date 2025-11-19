from django.urls import path
from .views import product_list, CrearProductoView, editar_producto

urlpatterns = [
    path('', product_list, name='product_list'),         # /api/products/
    path("nuevo/", CrearProductoView.as_view(), name="crear-producto"), # /api/products/nuevo/esta utiliza Vista basada en Clase.
    path("editar/<int:pk>/", editar_producto, name="editar-producto"), # /api/products/editar
]