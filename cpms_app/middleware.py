# gantt_app/middleware.py

from channels.auth import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
import json

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using session data.
    """
    async def authenticate(self, message):
        # Extract the user from the request's session and associate it with the WebSocket connection
        user = None
        token = message.get('user')
        if token:
            user = await self.get_user_by_token(token)
        return user

    async def get_user_by_token(self, token):
        try:
            user = await database_sync_to_async(User.objects.get)(token=token)
            return user
        except User.DoesNotExist:
            return None
        
    async def connect(self, event):
        # Authenticate the WebSocket connection
        user = await self.authenticate(self.scope)
        if user is None:
            await self.close()
        else:
            self.scope['user'] = user
            await super().connect(event)
