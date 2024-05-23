import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from django.utils.timesince import timesince

from .models import Message
from.templatetags.chatextras import initials


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # Receive message from WebSocket (frontend)
        text_data_json = json.loads(text_data)
        type = text_data_json["type"]
        message = text_data_json["message"]
        name = text_data_json["name"]
        agent = text_data_json.get("agent", "")

        print("Receive", type)

        if type == "message":
            # Send message to room group / room
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "chat_message", 
                    "message": message,
                    "name": name,
                    "agent": agent,
                    "initials": initials(name),
                    "created_at": timesince(new_message.created_at),
                }
            )


    async def chat_message(self, event):
        # Send message to WebSocket (frontend)
        await self.send(text_data=json.dumps({
            "type": event["type"],
            "message": event["message"],
            "name": event["name"],
            "agent": event["agent"],
            "initials": event["initials"],
            "created_at": event["created_at"],
        }))


    @sync_to_async
    def create_message(self, sent_by, message, agent):
        message = Message.objects.create()