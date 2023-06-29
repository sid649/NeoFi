import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.sender = self.scope['user']
        self.recipient_username = self.scope['url_route']['kwargs']['username']
        self.recipient = await self.get_recipient()

        if self.recipient is None:
            await self.close()
        else:
            self.room_name = self.get_room_name(self.sender.username, self.recipient_username)

            await self.channel_layer.group_add(
                self.room_name,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("Received Message" + text_data)
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        print("Server is replying")
        await self.send(text_data=json.dumps({
            'message': message + "from receiver -> " + str(self.recipient)
        }))

    @database_sync_to_async
    def get_recipient(self):

        try:
            return User.objects.get(username=self.recipient_username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_room_name(sender_username, recipient_username):
        if sender_username < recipient_username:
            return f'{sender_username}_{recipient_username}'
        else:
            return f'{recipient_username}_{sender_username}'