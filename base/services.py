from . models import ChatRoom, RoomMember
from django.contrib.auth.models import User


def get_or_create_group_chatroom(group_admin, users, group_name, visibility):
    room_type = 'group'
    room = ChatRoom.objects.create(
        name = group_name,
        room_type = room_type,
        visibility = visibility,
        created_by = group_admin,
    )

    RoomMember.objects.create(
        room = room,
        user = group_admin,
        is_admin = True
    )


    for user in users:
        RoomMember.objects.get_or_create(
            room = room,
            user = user
        )

    return room


def get_or_create_private_chatroom(user1, user2):
    room_type = 'private'

    room = (
        ChatRoom.objects
        .filter(room_type=room_type)
        .filter(members__user=user1)
        .filter(members__user=user2)
        .distinct()
        .first()
    )

    if room:
        return room

    room = ChatRoom.objects.create(
        room_type = room_type
    )
    
    RoomMember.objects.get_or_create(room = room,user = user1)
    RoomMember.objects.get_or_create(room = room,user = user2)

    return room