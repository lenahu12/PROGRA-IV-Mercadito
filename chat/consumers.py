import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Mensaje
from django.contrib.auth.models import AnonymousUser

from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.producto_id = self.scope['url_route']['kwargs']['producto_id']
        self.room_group_name = f"chat_{self.producto_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"Conexión WebSocket abierta para producto {self.producto_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        contenido = data['mensaje']
        autor = self.scope["user"]

        # Bloqueo si el usuario no está autenticado
        if autor is None or autor.is_anonymous:
            print("Intento de envío desde usuario no autenticado. Ignorado.")
            return

        # Guarda el mensaje en la base de datos
        await self.guardar_mensaje(autor, contenido)

        # Envía el mensaje al grupo WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "mensaje": contenido,
                "autor": autor.username
            }
        )


    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "mensaje": event["mensaje"],
            "autor": event["autor"]
        }))

    @sync_to_async
    def guardar_mensaje(self, autor, contenido):
        from products.models import Product
        producto = Product.objects.get(id=self.producto_id)
        Mensaje.objects.create(producto=producto, autor=autor, contenido=contenido)
