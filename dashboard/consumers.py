import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import pyautogui

class PhoneMouseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Import Django models inside method to avoid AppRegistryNotReady error
        from django.contrib.auth.models import Group
        user = self.scope["user"]
        if not user.is_authenticated or not (user.is_superuser or Group.objects.filter(user=user, name='admin').exists()):
            await self.close()
            return
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'move':
            dx = data.get('dx', 0)
            dy = data.get('dy', 0)
            await sync_to_async(pyautogui.moveRel)(dx, dy, duration=0)
        elif action == 'click':
            button = data.get('button', 'left')
            await sync_to_async(pyautogui.click)(button=button)
        elif action == 'down':
            button = data.get('button', 'left')
            await sync_to_async(pyautogui.mouseDown)(button=button)
        elif action == 'up':
            button = data.get('button', 'left')
            await sync_to_async(pyautogui.mouseUp)(button=button)
