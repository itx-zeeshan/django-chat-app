from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    UserListView,
    ChatRoomListCreateView,
    MyChatRoomsView,
    MessageListCreateView,
    LogoutView,
)

urlpatterns = [
    # 🔐 Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # 👤 Users
    path('users/', UserListView.as_view(), name='user_list'),

    # 💬 Chat Rooms
    path('rooms/', ChatRoomListCreateView.as_view(), name='room_list_create'),
    path('my-rooms/', MyChatRoomsView.as_view(), name='my_rooms'),

    # 📩 Messages
    path('messages/<int:room_id>/', MessageListCreateView.as_view(), name='messages_list_create'),
]