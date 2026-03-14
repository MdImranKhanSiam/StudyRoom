from django.shortcuts import render, redirect
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Max
import json
from . models import Room, Topic, Message, Participants, UserProfile, ChatRoom, ChatMessage, RoomMember
from . forms import RoomForm, RegisterForm
import cloudinary.uploader
from . services import get_or_create_group_chatroom, get_or_create_private_chatroom

# Create your views here.

def home(request):
    searched = request.GET.get('search')

    if searched == None:
        searched = ''
        
    rooms = Room.objects.filter(
        Q(topic__name__icontains=searched) |
        Q(name__icontains=searched) |
        Q(host__username__icontains=searched) |
        Q(description__icontains=searched)
    )

    if searched.isdigit():
        rooms = rooms | Room.objects.filter(id=searched)

    room_ids = rooms.values_list('id', flat=True)
    topics = Topic.objects.all()
    total_rooms = rooms.count()
    recent_messages = Message.objects.filter(room__id__in=room_ids)

    context = {
        'rooms' : rooms,
        'topics' : topics,
        'searched' : searched,
        'total_rooms' : total_rooms,
        'recent_messages' : recent_messages,
    }
    
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def room(request, the_id):
    current_room = Room.objects.get(id=the_id)
    room = ChatRoom.objects.get(id=current_room.chatroom.id)

    member = RoomMember.objects.filter(room=room, user=request.user).exists()

    if room.visibility == 'public' and not member:
        RoomMember.objects.get_or_create(
            room = room,
            user = request.user
            )
    
    members = room.members.all().order_by('-joined_at')

    context = {
        'room' : room,
        'members' : members,
        'studyroom' : current_room,
    }

    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def room_create(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)


        if form.is_valid():
            add_user = form.save(commit=False)
            add_user.host = request.user
            group_name = add_user.name # For get_or_create_group_chatroom
            
            # Add chatsystem after this

            extract_user_ids = request.POST.getlist('members')
            user_ids = list(map(int, extract_user_ids[0].split(",")))
            
            visibility = request.POST.get('visibility')
            users = User.objects.filter(id__in=user_ids)
            group_admin = request.user
            room = get_or_create_group_chatroom(group_admin, users, group_name, visibility)
            
            add_user.chatroom = room

            add_user.save()

            return redirect('Homepage')

    context = {
        'form' : form
    }

    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def room_edit(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user == room.host:
        if request.method == 'POST':
            form = RoomForm(request.POST, instance=room)

            if form.is_valid():
                form.save()
                return redirect('Homepage')
    else:
        return HttpResponse('You are not allowed to edit this room.')

    context = {
        'room' : room,
        'form' : form,
    }

    return render(request, 'base/room_edit_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user == room.host:
        if request.method == 'POST':
            room.chatroom.delete()
            return redirect('Homepage')
    else:
        return HttpResponse('You are not allowed to delete this room')

    context = {
        'item' : room.name,
    }

    return render(request, 'base/delete.html', context)

def register_user(request):
    if request.user.is_authenticated:
        return redirect('Homepage')
    
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            current_user = form.save()
            UserProfile.objects.create(
                user = current_user,
                display_name = current_user.username,
            )
            login(request, current_user)
            return redirect('Homepage')
        else:
            messages.error(request, 'An error occurred during registration')

    context = {
        'form' : form,
    }
    return render(request, 'base/login_registration.html', context)


def login_user(request):
    page_type = 'login'
    if request.user.is_authenticated:
        return redirect('Homepage')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Homepage')
        else:
            messages.error(request, 'Username or Password is invalid')

    context = {
        'page_type' : page_type,
    }
    return render(request, 'base/login_registration.html', context)

def logout_user(request):
    logout(request)
    return redirect('Homepage')

@login_required(login_url='login')
def delete_message(request, pk):
    message = ChatMessage.objects.get(id=pk)

    if request.user == message.sender:
        if request.method == 'POST':
            message.delete()
            next_url = request.POST.get('next')

            return redirect(next_url)
    else:
        return HttpResponse('You are not allowed to delete this message.')
        
    context = {
        'item' : message.content,
    }

    return render(request, 'base/delete.html', context)


# chats = current_room.message_set.all().order_by('-created')

@login_required(login_url='login')
def user_profile(request, pk):
    locate_user = User.objects.get(id=pk)

    this_profile_user = UserProfile.objects.get(user=locate_user)
    users_rooms = locate_user.room_set.all().order_by('-created')
    total_rooms = users_rooms.count()
    users_messages = locate_user.message_set.all().order_by('-created')[:25]

    if request.user == locate_user:
        if request.method == 'POST':
            if request.FILES.get('update_avatar_data'):
                user_image = request.FILES.get('update_avatar_data')
                response = cloudinary.uploader.upload(
                    user_image,
                    resource_type = "image"
                )
                this_profile_user.avatar = response.get("secure_url")

            if request.POST.get('display_name'):
                this_profile_user.display_name = request.POST.get('display_name')

            if request.POST.get('bio'):
                this_profile_user.bio = request.POST.get('bio')

            if request.POST.get('gender'):
                this_profile_user.gender = request.POST.get('gender')

            if request.POST.get('date_of_birth'):
                this_profile_user.date_of_birth = request.POST.get('date_of_birth')
            
            if request.POST.get('country'):
                this_profile_user.country = request.POST.get('country')

            this_profile_user.save()

            return redirect('user_profile', pk)
            
    total = range(15)

    context = {
        'this_profile_user' : this_profile_user,
        'total' : total,
        'users_rooms' : users_rooms,
        'total_rooms' : total_rooms,
        'users_messages' : users_messages,
    }

    return render(request, 'base/user_profile.html', context)

# def user_profile_update(request, pk):
#     locate_user = User.objects.get(id=pk)

#     this_profile_user = None

#     context = {
#         'this_profile_user' : this_profile_user,
#     }

#     return render(request, 'base/user_profile_update.html', context)


# Chatsystem

@login_required(login_url='login')
def search_users(request):
    username = request.GET.get("username", "").strip()
    users = User.objects.filter(username__icontains=username, is_superuser=False).exclude(id=request.user.id)[:5]
    data = list(users.values("id", "username"))

    return JsonResponse(data, safe=False)


@login_required(login_url='login')
def chat_room(request, room_id):
    room = ChatRoom.objects.get(id=room_id)
    members = room.members.all().order_by('-joined_at')
    context = {
        'room' : room,
        'members' : members,
    }

    return render(request, 'base/chat_room.html', context)

@login_required(login_url='login')
def fetch_messages(request, room_id):
    page_number = request.GET.get('page', 1)
    messages = ChatMessage.objects.filter(room_id=room_id).order_by('-timestamp')

    if int(page_number) == 1:
        membership = RoomMember.objects.get(room__id=room_id, user=request.user)
        membership.last_read = messages[0].timestamp
        membership.save(update_fields=['last_read'])
    
    paginator = Paginator(messages, 20)
    page = paginator.get_page(page_number)
    data = []

    for m in page:
        try:
            avatar = m.sender.userprofile.avatar
        except UserProfile.DoesNotExist:
            avatar = None

        data.append({
            'sender_id': m.sender.id,
            'sender_name': m.sender.username,
            'sender_avatar': avatar,
            'content': m.content,
            'timestamp': m.timestamp.strftime("%Y-%m-%d %H:%M")
            # 'timestamp': m.timestamp.isoformat()
        })

    return JsonResponse({
        'messages' : data,
        'has_next' : page.has_next()
    })






@login_required(login_url='login')
def people(request):
    search = request.GET.get('search_people')
    searched = request.GET.get('searched')
    
    searching = search or searched

    if not searching:
        searching = 'all_users'

    users = None

    if searching == 'all_users':
        users = User.objects.filter(is_superuser=False).exclude(id=request.user.id)
    elif searching == 'friends':
        None
    elif searching == 'following':
        None
    elif searching == 'followers':
        None
    elif searching == 'friend_requests':
        None
    else:
        users = User.objects.filter(username__icontains=searching, is_superuser=False).exclude(id=request.user.id)[:20]

    # found_users = list(users.values("id", "username", "userprofile__display_name", "userprofile__avatar"))

    context = {
        'found_users' : users,
    }

    return render(request, 'base/people.html', context)


def search_people(request):
    username = request.GET.get("username", "").strip()
    users = User.objects.filter(username__icontains=username, is_superuser=False).exclude(id=request.user.id)[:30]
    data = list(users.values("id", "username", "userprofile__display_name", "userprofile__avatar"))

    return JsonResponse(data, safe=False)



@login_required(login_url='login')
def private_chat(request, user_id):
    user2 = User.objects.get(id=user_id)

    room = get_or_create_private_chatroom(request.user, user2)

    context = {
        'user2' : user2,
        'room' : room,
    }


    
    return render(request, 'base/private_chat.html', context)

@login_required(login_url='login')
def fetch_chatmessages(request, chatroom_id):
    before = request.GET.get('before')
    room = ChatRoom.objects.get(id=chatroom_id)

    # print(f'Visibility: {room.visibility}')

    member = RoomMember.objects.filter(room=room, user=request.user).exists()

    if room.visibility == 'private' and not member:
        return HttpResponse("Good try buddy but you can't hack this database hahaha😂, keep trying🥱")

    older_messages = ChatMessage.objects.filter(room=room)

    if before:
        older_messages = older_messages.filter(timestamp__lt=before)
    

    older_messages = older_messages.order_by('-timestamp')[:25]

    if not before:
        membership = RoomMember.objects.get(room=room, user=request.user)
        membership.last_read = older_messages[0].timestamp
        membership.save(update_fields=['last_read'])
       

    data = []

    for m in older_messages:
        data.append(
            {
                'message_id': m.id,
                'sender_id': m.sender.id,
                'sender_name': m.sender.username,
                'sender_avatar': m.sender.userprofile.avatar,
                'sender_display_name': m.sender.userprofile.display_name,
                'content': m.content,
                'timestamp': m.timestamp
            }
        )

    return JsonResponse(
        {
            'older_messages': data,
            'has_more': len(older_messages) == 25
        }
    )


@login_required(login_url='login')
def inbox(request):

    return render(request, 'base/inbox.html')

@login_required(login_url='login')
def fetch_inbox(request):
    # rooms = ChatRoom.objects.filter(members__user=request.user).distinct()

    rooms = (
        ChatRoom.objects
        .filter(members__user=request.user)
        .annotate(last_message_time=Max('messages__timestamp'))
        .order_by('-last_message_time')
        .distinct()
    )

    data = []

    for room in rooms:
        latest_message = None

        try:
            latest_message = room.messages.last()
            latest_msg = latest_message.content
            latest_msg_time = latest_message.timestamp
            latest_msg_sender = latest_message.sender

            if latest_message.sender == request.user:
                latest_msg_sender = 'You'
            else:
                latest_msg_sender = latest_message.sender.userprofile.display_name
        
            # print(f'Latest Message: {latest_message}')
            # latest_message = latest_message.content
            unread_count = 0
            member = room.members.get(user=request.user)

            if member.last_read:
                unread_count = room.messages.filter(
                    timestamp__gt=member.last_read
                ).exclude(
                    sender=request.user
                ).count()
            else:
                unread_count = room.messages.exclude(sender=request.user).count()

            if room.room_type == 'private':
                other_user = User.objects.filter(chat_rooms__room=room).exclude(id=request.user.id)
                other_user = other_user[0]

                data.append(
                    {
                        'room_type': room.room_type,
                        'visibility': room.visibility,
                        'id': other_user.id,
                        'username': other_user.username,
                        'display_name': other_user.userprofile.display_name,
                        'avatar': other_user.userprofile.avatar,
                        'latest_msg': latest_msg,
                        'latest_msg_time': latest_msg_time,
                        'latest_msg_sender': latest_msg_sender,
                        'unread_count': unread_count,
                    }
                )
            else:
                current_room = None

                try:
                    current_room = room.study_rooms

                    data.append(
                        {
                            'id': current_room.id,
                            'room_type': room.room_type,
                            'visibility': room.visibility,
                            'host_username': current_room.host.userprofile.display_name,
                            'host_avatar': current_room.host.userprofile.avatar,
                            'room_name': current_room.name,
                            'topic': current_room.topic.name,
                            'created': current_room.created,
                            'latest_msg': latest_msg,
                            'latest_msg_time': latest_msg_time,
                            'latest_msg_sender': latest_msg_sender,
                            'unread_count': unread_count
                        }
                    )
                except:
                    current_room = 'Not found'
        
        except:
            latest_message = ''
        
        

    send = {
        "total_rooms": rooms.count(),
        "rooms": data,
    }

    return JsonResponse(send)
