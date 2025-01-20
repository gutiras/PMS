from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.apps import apps
import json
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
from io import BytesIO

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Set up the room name and group name for this chat room.
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Dynamically load the ChatRoom model and get or create the chat room.
        ChatRoom = apps.get_model('gantt_app', 'ChatRoom')
        self.chat_room = await database_sync_to_async(ChatRoom.objects.get_or_create)(
            name=self.room_name
        )

        # Add this WebSocket connection to the chat group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # When the WebSocket disconnects, remove the connection from the group.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse the incoming JSON data from the WebSocket.
        data = json.loads(text_data)

        # Dynamically load the Message model.
        Message = apps.get_model('gantt_app', 'Message')

        # If the data includes a file, process and store it.
        file_data = data.get('file')
        file_name = data.get('file_name')
       
        if file_data:
            # Save the file and get the file path.
            file_path = await database_sync_to_async(self.save_file)(file_data, file_name)
            data['file'] = file_path  # Add file path to the data
        
        # Create the message in the database (include the reply if any).
        await database_sync_to_async(self.create_message)(data)

        # Broadcast the message to all users in the room.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data.get('content'),
                'reply_to': data.get('reply_to'),  # Include reply details
                'file': data.get('file'),
                'user': data.get('user'),
                'timestamp': data.get('timestamp')
            }
        )

    def create_message(self, data):
        from django.apps import apps
        
        # Get the Message model
        Message = apps.get_model('gantt_app', 'Message')
        
        # Get the authenticated user
        user = self.scope['user'] if self.scope['user'].is_authenticated else None
        
        # Get the chat room (first element of the room list, as you have implemented it)
        chat_room = self.chat_room[0]
        
        # Initialize variables
        reply_to_message = None
        
        # Validate and fetch reply_to_message
        reply_to_id = data.get('reply_to')
        if reply_to_id:
            try:
                # Ensure reply_to_id is an integer
                reply_to_message = Message.objects.get(id=int(reply_to_id))
            except (ValueError, Message.DoesNotExist):
                # If it's invalid or doesn't exist, log an error (optional)
                print(f"Invalid reply_to ID: {reply_to_id}")
                reply_to_message = None
        
        # Create the new message
        Message.objects.create(
            room=chat_room,
            user=user,
            content=data.get('content', ''),  # Default to empty string if no content
            reply_to=reply_to_message,
            file=data.get('file', None)  # Default to None if no file is provided
        )

    async def chat_message(self, event):
        # Extract the message details from the event.
        Message = apps.get_model('gantt_app', 'Message')
        message = event['message']
        reply_to = event.get('reply_to')
        file_data = event.get('file', None)
        user = event['user']
        timestamp = event['timestamp']
        print(reply_to)
        # If a file exists, generate its URL based on MEDIA_URL.
        file_url = f"{settings.MEDIA_URL}{file_data}" if file_data else None
        
        # Send the message back to the WebSocket.
        await self.send(text_data=json.dumps({
            'message': message,
            'reply_to': reply_to,
            'file': file_url,  # Send the full file URL to the client
            'user': user,
            'timestamp': timestamp
        }))

    @staticmethod
    def save_file(base64_file, file_name):
        """
        Save a base64-encoded file to the disk and return the file path.
        """
        try:
            # Decode the base64 file data.
            file_content = base64.b64decode(base64_file)

            # Generate a path for the file in storage.
            file_path = f'chat_files/{file_name}'

            # Save the file using Django's default storage backend.
            file = ContentFile(file_content)
            file_path = default_storage.save(file_path, file)

            return file_path
        except Exception as e:
            # Log any errors (you can use logging instead of print statements in production).
            print(f"Error saving file: {str(e)}")
            return None  # Return None in case of an error

