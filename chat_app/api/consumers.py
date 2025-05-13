from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings
from django.contrib.auth import get_user_model

@sync_to_async
def get_user(user_id):
    return get_user_model().objects.get(id=user_id)

async def validate_token(token):
    try:
        token_backend = TokenBackend(algorithm='HS256', signing_key=settings.SECRET_KEY)
        payload = token_backend.decode(token, verify=True)
        user = await get_user(payload.get("user_id"))
        return user
    except Exception as e:
        print("Token validation error:", e)
        return None


def save_message(sender_id, receiver_id, content):
    from .models import User, ChatRoom, Message

    try:
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        room = ChatRoom.objects.filter(members=sender).filter(members=receiver).first()

        if not room:
            room = ChatRoom.objects.create(name=f"{sender.username}_{receiver.username}")
            room.members.add(sender, receiver)

        Message.objects.create(
            room=room,
            sender=sender,
            receiver=receiver,
            content=content,
            timestamp=now()
        )
    except Exception as e:
        print("Save error:", e)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            await self.send(json.dumps({"type": "error", "message": f"Connection error: {str(e)}"}))
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Disconnect error: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            token = data.get('token')
            event_type = data.get('type', 'message')

            if not token:
                raise ValueError("Token is missing.")

            # Validate token
            auth_response = await validate_token(token)
            if not auth_response:
                raise PermissionError("Invalid or expired token.")

            print("Auth response:", auth_response)
            user_id = auth_response.id
            username = auth_response.username

            if event_type == 'message':
                message = data.get('message')
                receiver = data.get('receiver')

                if not message or not receiver:
                    raise ValueError("Missing message or receiver.")

                # Save message
                try:
                    save_message(user_id, receiver, message)
                except Exception as save_error:
                    raise Exception(f"Error saving message: {str(save_error)}")

                # Broadcast
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': user_id,
                        'receiver': receiver,
                    }
                )

            elif event_type == 'typing':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_typing',
                        'sender': user_id,
                    }
                )

            elif event_type == 'join':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_joined',
                        'username': username,
                    }
                )

            elif event_type == 'exit':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_left',
                        'username': username,
                    }
                )

            else:
                raise ValueError(f"Unsupported event type: {event_type}")

        except ValueError as ve:
            await self.send(json.dumps({"type": "error", "message": str(ve)}))
            await self.close()

        except PermissionError as pe:
            await self.send(json.dumps({"type": "unauthorized", "message": str(pe)}))
            await self.close()

        except Exception as e:
            await self.send(json.dumps({"type": "error", "message": f"Server error: {str(e)}"}))
            await self.close()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event["message"],
            "sender": event["sender"],
            "receiver": event["receiver"]
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "sender": event['sender']
        }))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            "type": "join",
            "username": event['username']
        }))

    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            "type": "exit",
            "username": event['username']
        }))
