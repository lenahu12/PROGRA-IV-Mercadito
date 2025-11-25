from django.db import models
from products.models import Product
from users.models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()
class Compra(models.Model):
    comprador = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Compra #{self.id} - {self.comprador.email}"

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
class CarritoTemporal(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.JSONField()  # guarda el carrito como JSON
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.email} ({self.creado})"