import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_username = self.scope["url_route"]["kwargs"]["username"]
        self.sender_username = self.scope["user"].username
        users = sorted([self.receiver_username, self.sender_username])
        self.room_group_name = f"chat_{users[0]}_{users[1]}"

        await self.channel_layer.group_add(  # type: ignore
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(  # type: ignore
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = self.scope["user"]
        receiver = await User.objects.aget(username=self.receiver_username)

        await ChatMessage.objects.acreate(
            sender=sender, receiver=receiver, message=message
        )

        await self.channel_layer.group_send(  # type: ignore
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
