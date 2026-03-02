from django.contrib import admin

# Register your models here.

from . models import Room, Topic, Message, Participants, UserProfile, ChatRoom, GroupInvite, RoomMember, ChatMessage

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Participants)
admin.site.register(UserProfile)

# Chatsystem
admin.site.register(ChatRoom)
admin.site.register(GroupInvite)
admin.site.register(RoomMember)
admin.site.register(ChatMessage)
