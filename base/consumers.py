import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    # Initializing handshake
    async def connect(self):
        # print(self.scope)

        self.user = self.scope['user']
        self.avatar = await self.get_user_avatar(self.user.id)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'chat_{self.room_id}'

        if not self.user.is_authenticated:
            await self.close()
            return
        
        if not await self.is_room_member():
            await self.close()
            return
        
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
        data = json.loads(text_data)

        if data['type'] == 'message':
            message = await self.save_message(data['message'])
            avatar = await self.get_user_avatar(message['sender_id'])

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type' : 'chat_message',
                    'message' : message,
                    'user_avatar' : avatar
                }
            )
        elif data['type'] == 'typing':

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type' : 'typing',
                    'user' : self.user.username,
                    'user_id' : self.user.id,
                    'user_avatar' : self.avatar
                }
            )
        elif data['type'] == 'delete_message':
            message_id = data['message_id']
            
            deleted = await self.delete_message(message_id)

            if deleted:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type' : 'message_deleted',
                        'message_id' : message_id
                    }
                )



    @database_sync_to_async
    def get_user_avatar(self, users_id):
        from . models import UserProfile

        return UserProfile.objects.only("avatar").get(user_id=users_id).avatar
        


    @database_sync_to_async
    def is_room_member(self):
        from . models import RoomMember
        exists = RoomMember.objects.filter(
            room_id = self.room_id,
            user = self.user
        ).exists()

        return exists
    
    @database_sync_to_async
    def save_message(self, message):
        from . models import ChatMessage
        new_message = ChatMessage.objects.create(
            room_id = self.room_id,
            sender = self.user,
            content = message
        )

        message_info = {
            'message_id' : new_message.id,
            'sender_id' : new_message.sender.id,
            'sender_name' : new_message.sender.username,
            'content' : new_message.content,
            'timestamp' : new_message.timestamp.isoformat(),
        }

        return message_info
    
    @database_sync_to_async
    def delete_message(self, message_id):
        from . models import ChatMessage
        msg = ChatMessage.objects.get(id=message_id)

        if msg.sender == self.user:
            msg.delete()
            return True
        else:
            return False
    
    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps({
                'type' : 'message',
                'message' : event['message'],
                'user_avatar' : event['user_avatar']
            })
        )

    async def typing(self, event):
        if event['user'] != self.user.username:
            await self.send(
                text_data=json.dumps({
                    'type' : 'typing',
                    'user' : event['user'],
                    'user_id' : event['user_id'],
                    'user_avatar' : event['user_avatar']
                })
            )

    async def message_deleted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    'type' : 'delete_message',
                    'message_id' : event['message_id']
                }
            )
        )











































# For public room
class PublicChatConsumer(AsyncWebsocketConsumer):

    # Initializing handshake
    async def connect(self):
        # print(self.scope)

        self.user = self.scope['user']
        self.avatar = await self.get_user_avatar(self.user.id)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'chat_{self.room_id}'

        if not self.user.is_authenticated:
            await self.close()
            return
        
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
        data = json.loads(text_data)

        if data['type'] == 'message':
            message = await self.save_message(data['message'])
            avatar = await self.get_user_avatar(message['sender_id'])

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type' : 'chat_message',
                    'message' : message,
                    'user_avatar' : avatar
                }
            )
        elif data['type'] == 'typing':

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type' : 'typing',
                    'user' : self.user.username,
                    'user_id' : self.user.id,
                    'user_avatar' : self.avatar
                }
            )
        elif data['type'] == 'delete_message':
            message_id = data['message_id']
            
            deleted = await self.delete_message(message_id)

            if deleted:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type' : 'message_deleted',
                        'message_id' : message_id
                    }
                )


    @database_sync_to_async
    def get_user_avatar(self, users_id):
        from . models import UserProfile

        return UserProfile.objects.only("avatar").get(user_id=users_id).avatar
        
    
    @database_sync_to_async
    def save_message(self, message):
        from . models import ChatMessage
        new_message = ChatMessage.objects.create(
            room_id = self.room_id,
            sender = self.user,
            content = message
        )

        message_info = {
            'message_id' : new_message.id,
            'sender_id' : new_message.sender.id,
            'sender_name' : new_message.sender.username,
            'content' : new_message.content,
            'timestamp' : new_message.timestamp.isoformat(),
        }

        return message_info
    

    @database_sync_to_async
    def delete_message(self, message_id):
        from . models import ChatMessage
        msg = ChatMessage.objects.get(id=message_id)

        if msg.sender == self.user:
            msg.delete()
            return True
        else:
            return False



    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps({
                'type' : 'message',
                'message' : event['message'],
                'user_avatar' : event['user_avatar']
            })
        )

    async def typing(self, event):
        if event['user'] != self.user.username:
            await self.send(
                text_data=json.dumps({
                    'type' : 'typing',
                    'user' : event['user'],
                    'user_id' : event['user_id'],
                    'user_avatar' : event['user_avatar']
                })
            )

    async def message_deleted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    'type' : 'delete_message',
                    'message_id' : event['message_id']
                }
            )
        )