import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Thread, ChatMessage

# Obtiene el modelo de usuario activo en el proyecto
User = get_user_model()

class ChatConsumer(AsyncConsumer):
    # Se ejecuta cuando un cliente WebSocket intenta conectarse
    async def websocket_connect(self, event):
        print('conectado', event)
        # Obtiene el usuario logueado
        user = self.scope['user']
        # Crea el nombre del grupo de chat para el usuario
        chat_room = f'user_chatroom_{user.id}'
        # Asigna el nombre del grupo de chat al canal actual
        self.chat_room = chat_room
        # Agrega el canal actual al grupo de chat
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        # Acepta la conexión WebSocket
        await self.send({
            'type': 'websocket.accept'
        })

    # Se ejecuta cuando se recibe un mensaje del cliente WebSocket
    async def websocket_receive(self, event):
        print('recibido', event)
        
        # Convierte el texto JSON recibido en un diccionario de Python
        received_data = json.loads(event['text'])
        
        # Agregar log para debug
        print("Datos recibidos:", received_data)
        
        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')

        # Agregar log para debug
        print(f"Intentando enviar mensaje de usuario {sent_by_id} a usuario {send_to_id}")
        
        # Si no hay mensaje, termina la función
        if not msg:
            print('No hay mensaje')
            return False
        
        # Obtiene los objetos de los usuarios
        sent_by_user = await self.get_user_object(sent_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        # Si no se encuentra el usuario que envió el mensaje, termina la función
        if not sent_by_user:
            print('sent by user no encontrado')
            return False  # Agregar return
        if not send_to_user:
            print('send to user no encontrado')
            return False  # Agregar return
        if not thread_obj:
            print('thread no encontrado')
            return False
        
        # Crea el mensaje en la base de datos
        await self.create_chat_message(thread_obj, sent_by_user, msg)
        
        # Crea el nombre del grupo de chat para el usuario al que se le envía el mensaje
        other_user_chat_room = f'user_chatroom_{send_to_id}'

        # Prepara la respuesta con el mismo mensaje
        response = {
            'message': msg,
            'sent_by': sent_by_id,  # Usar sent_by_id en lugar de self_user.id
            'send_to': send_to_id,
            'thread_id': thread_id
        }

        print(f"Enviando mensaje a sala {other_user_chat_room}")
        # Envía el mensaje al grupo de chat del usuario al que se le envía el mensaje
        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        # Envía el mensaje al grupo de chat del usuario que envió el mensaje
        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    # Se ejecuta cuando el cliente WebSocket se desconecta
    async def websocket_disconnect(self, event):
        print('desconectado', event)

    # Se ejecuta cuando se recibe un mensaje del grupo de chat
    async def chat_message(self, event):
        print('chat_message', event)
        # Envía el mensaje al cliente WebSocket
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    # esta funcion sirve para obtener un usuario por su ID
    @database_sync_to_async
    def get_user_object(self, user_id):
        # Obtiene el usuario con el ID proporcionado
        # qs es una lista de usuarios y significa QuerySet
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg):
        ChatMessage.objects.create(thread=thread, user=user, message=msg)