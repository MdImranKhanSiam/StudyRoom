from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='Homepage'),
    path('room/<str:the_id>/', views.room, name='Room'),
    path('room_create/', views.room_create, name='room_create'),
    path('room_edit/<str:pk>/', views.room_edit, name='room_edit'),
    path('delete_room/<str:pk>/', views.delete_room, name='delete-room'),
    path('login/', views.login_user, name='login'),
    path('registration/', views.register_user, name='registration'),
    path('logout/', views.logout_user, name='logout'),
    path('delete_message/<str:pk>/', views.delete_message, name='delete-message'),
    path('user_profile/<str:pk>/', views.user_profile,name='user_profile'),
    # path('user_profile_view/<str:pk>', views.user_profile_update,name='user_profile'),
    path('people/', views.people, name='people'),
    path('search_people/', views.search_people, name='search-people'),

    # Chatsystem
    path('search_users/', views.search_users, name='search-users'),
    path('chat_room/<int:room_id>/', views.chat_room, name='chat-room'),
    path('messages/<int:room_id>/', views.fetch_messages, name='fetch-messages'),
    path('chatmessages/<int:chatroom_id>/', views.fetch_chatmessages, name='fetch-chatmessages'),
    path('message/<int:user_id>/', views.private_chat, name='private-chat'),
    path('inbox/', views.inbox, name='inbox'),
    path('fetch_inbox/', views.fetch_inbox, name='fetch-inbox'),
]

