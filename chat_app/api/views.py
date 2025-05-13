from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, ChatRoom, Message
from .serializers import UserSerializer, ChatRoomSerializer, MessageSerializer
from django.db import IntegrityError

# 🔐 Login
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'success': False, 'message': 'Both email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            return Response({'success': False, 'message': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'message': 'User logged in successfully!',
            'data': {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }
        }, status=status.HTTP_200_OK)
    
# 🔐 Register
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({
                    'success': True,
                    'data': {
                        'id': user.id,
                        'username': user.username
                    },
                    'message': 'User registered successfully!'
                }, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({
                    'success': False,
                    'message': 'User already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Unexpected error: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        first_error = next(iter(serializer.errors.values()))[0]
        return Response({
            'success': False,
            'message': first_error
        }, status=status.HTTP_400_BAD_REQUEST)

# 🔐 Logout
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({
                    'success': False,
                    'message': 'Refresh token is required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'success': True,
                'message': 'Logged out successfully!'
            }, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return Response({
                'success': False,
                'message': f'Logout failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

# 👤 List all users
class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.all().values('id', 'username')
        return Response({
            'success': True,
            'data': list(users),
            'message': 'User list fetched successfully.'
        }, status=status.HTTP_200_OK)

# 💬 Create and list all rooms
class ChatRoomListCreateView(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        rooms = self.get_queryset()
        serializer = self.get_serializer(rooms, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'All chat rooms fetched successfully.'
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            room.members.add(request.user)
            return Response({
                'success': True,
                'data': self.get_serializer(room).data,
                'message': 'Chat room created successfully.'
            }, status=status.HTTP_201_CREATED)

        first_error = next(iter(serializer.errors.values()))[0]
        return Response({
            'success': False,
            'message': first_error
        }, status=status.HTTP_400_BAD_REQUEST)

# 💬 List current user's rooms
class MyChatRoomsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rooms = request.user.chat_rooms.all()
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Your chat rooms fetched successfully.'
        }, status=status.HTTP_200_OK)

# 📩 List/Create messages in a specific room
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(room_id=self.kwargs['room_id']).order_by('timestamp')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Messages fetched successfully.'
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Message sent successfully.'
            }, status=status.HTTP_201_CREATED)

        first_error = next(iter(serializer.errors.values()))[0]
        return Response({
            'success': False,
            'message': first_error
        }, status=status.HTTP_400_BAD_REQUEST)
