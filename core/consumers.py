import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

# Obtiene el modelo de usuario activo en el proyecto
User = get_user_model()

class ChatConsumer(AsyncConsumer):
    # Se ejecuta cuando un cliente WebSocket intenta conectarse
    async def websocket_connect(self, event):
        print('conectado', event)
        # Acepta la conexión WebSocket
        await self.send({
            'type': 'websocket.accept'
        })

    # Se ejecuta cuando se recibe un mensaje del cliente WebSocket
    async def websocket_receive(self, event):
        print('recibido', event)
        # Convierte el texto JSON recibido en un diccionario de Python
        received_data = json.loads(event['text'])
        # Obtiene el mensaje del diccionario
        msg = received_data.get('message')
        
        # Si no hay mensaje, termina la función
        if not msg:
            return False
        
        # Prepara la respuesta con el mismo mensaje
        response = {
            'message': msg
        }
        
        # Envía la respuesta de vuelta al cliente WebSocket
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(response)  # Convierte el diccionario a JSON
        })

    # Se ejecuta cuando el cliente WebSocket se desconecta
    async def websocket_disconnect(self, event):
        print('desconectado', event)