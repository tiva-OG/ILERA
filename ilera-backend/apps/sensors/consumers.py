from channels.generic.websocket import AsyncWebsocketConsumer
import json


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        self.device_id = self.scope["url_route"]["kwargs"]["device_id"]

        if not user.is_authenticated:
            self.close()

        self.group_name = f"device_{self.device_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_layer_alias)

    async def send_reading(self, event):
        await self.send(text_data=json.dumps(event["reading"]))
