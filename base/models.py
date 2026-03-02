from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

# Chat System

default_avatar = "https://res.cloudinary.com/dxd9uxsfv/image/upload/v1770963972/bjngg2xwjfd0vp69xv45.jpg"

class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )

    VISIBILITY_CHOICES = (
        ('private', 'Private'),

        ('public', 'Public'),
    )

    name = models.CharField(max_length=255, default='private_room')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    # Force saves room_type as private for private chat room
    # def save(self, *args, **kwargs):
    #     if self.room_type == 'private':
    #         self.visibility = 'private'
        
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}: {self.id}'
    


class GroupInvite(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)



class RoomMember(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    is_admin = models.BooleanField(default=False)
    last_read = models.DateTimeField(default=timezone.now)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'user'],
                name='unique_room_user'
            )
        ]


    def __str__(self):
        return f'{self.user.username} in {self.room.name} : {self.room.id}'
    


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['room', 'timestamp']
            ),
        ]

        ordering = ['timestamp']
        

    def __str__(self):
        return f'{self.sender} -> {self.room.name}: {self.room.id} -> {self.content}'




# Chat System






class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.id} : {self.name}'


class Room(models.Model):
    chatroom = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name='study_rooms', null=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)
    # participants = models.ManyToManyField(User,related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return f'{self.name}: {self.host}'
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return f'{self.body[:30]}: {self.id}'
    
class Participants(models.Model):
    user_name_room = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_name_room')
    user_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='user_room')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user_name_room}'
    

class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),

        ('female', 'Female'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=200, null=True, blank=True)
    avatar = models.URLField(blank=True, null=True, default=default_avatar)
    bio = models.TextField(max_length=1000, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=300, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    social = models.URLField(blank=True, null=True)


    
    