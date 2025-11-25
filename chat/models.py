from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Mensaje(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="mensajes")
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.autor.username} → {self.producto.nombre}"