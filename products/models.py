from django.db import models
from django.conf import settings


CATEGORIAS = [
    ('farmacos', 'Fármacos'),
    ('bebidas', 'Bebidas'),
    ('lacteos', 'Lácteos'),
    ('carnes_pescados', 'Carnes y Pescados'),
    ('frutas_verduras', 'Frutas y Verduras'),
    ('limpieza', 'Limpieza'),
    ('snacks', 'Snacks'),
    ('otros', 'Otros'),
]

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS, blank=False, default='Otros')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)



