from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatMessage
from django.contrib.auth import get_user_model


User = get_user_model()


# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_id = self.scope['url_route']['kwargs']['user_id']
#         self.user = await self.get_user(self.user_id)

#         if not self.user:
#             await self.close()
#             return

#         await self.channel_layer.group_add(self.user_id, self.channel_name)
#         await self.accept()


#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.user_id, self.channel_name)


#     async def receive(self, text_data):
#         message = text_data

#         if self.user.status == 'online':
#             await self.send_chat_message(message)
#         else:
#             await self.send_status_error()


#     async def send_chat_message(self, message):
#         await self.channel_layer.group_send(
#             self.user_id,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )


#     async def send_status_error(self):
#         await self.send(text_data='The user is offline.')


#     async def chat_message(self, event):
#         message = event['message']
#         await self.send(text_data=message)


#     @staticmethod
#     async def get_user(user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None
        


class SendChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['user'].id
        self.chat = await self.get_chat(self.chat_id)

        if self.chat:
            self.room_group_name = f'chat_{self.chat_id}'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user']
        receiver = text_data_json['receiver']

        # Create and save the message
        new_message = ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)

        # Notify the other participant about the new message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'created_at': new_message.created_at.isoformat(),
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        created_at = event['created_at']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'created_at': created_at,
        }))

    @staticmethod
    async def get_chat(chat_id):
        try:
            return ChatMessage.objects.get(id=chat_id)
        except ChatMessage.DoesNotExist:
            return None