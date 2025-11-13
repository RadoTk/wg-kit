import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrdersNotificationAdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'orders_admin'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def send_new_order(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'message': event['message'],
        }))

    async def send_payment_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'payment',
            'message': event['message'],
        }))
