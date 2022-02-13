from unicodedata import name
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
# Create your views here.

@login_required(login_url='login')
def user_profile(req, pk):
    user = User.objects.get(pk=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = user.message_set.all()
    context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_messages': room_messages}
    return render(req, 'base/profile.html',context )


@login_required(login_url='login')
def update_profile(req):
    user = req.user
    form = UserForm(instance=user)
    
    if req.method == 'POST':
        form = UserForm(req.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', user.id)
    
    context = {'user': user, 'form': form}
    return render(req, 'base/update-profile.html', context)
""""
Home controller
"""
def home(req):
    query = req.GET.get('q') if req.GET.get('q') !=None else ''
    
    
    rooms = Room.objects.all()
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )
    
    
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=query))
    
    rooms__count = rooms.count()
    
    context = {'rooms': rooms, 'topics': topics, 'rooms__count': rooms__count, 'room_messages': room_messages}

    return render(req, 'base/home.html', context)


def room(req, pk):
    room = Room.objects.get(pk=pk)
    room_messages = room.message_set.all().order_by('-created_at')
    participants = room.participants.all()
    
    if req.method == 'POST':
        message = Message.objects.create(
            user = req.user,
            room = room,
            body = req.POST.get('body')
        )
        room.participants.add(req.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(req, 'base/room.html', context)

@login_required(login_url='login')
def create_room(req):
    form = RoomForm()
    topics = Topic.objects.all()
    if req.method == 'POST':
        topic_name = req.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = req.user,
            topic = topic,
            name = req.POST.get('name'),
            description = req.POST.get('description'),
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(req, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(req, pk):
    print(pk)
    room = Room.objects.get(pk=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if req.user != room.host:
        return HttpResponse('You are not allowed to edit this room')
    
    
    if req.method == 'POST':
        topic_name = req.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = req.POST.get('name')
        room.description = req.POST.get('description')
        
        room.save()
        return redirect('home')
        # form = RoomForm(req.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(req, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(req, pk):
    room = Room.objects.get(pk=pk)
    
    if req.user != room.host:
        return HttpResponse('You are not allowed to edit this room')
    
    if req.method == 'POST':
        room.delete()
        return redirect('home')
    return render(req, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def delete_message(req, pk):
    message = Message.objects.get(pk=pk)
    
    if req.user != message.user:
        return HttpResponse('You are not allowed to edit this room')
    
    if req.method == 'POST':
        message.delete()
        return redirect('home')
    return render(req, 'base/delete.html', {'obj': message})


def login_page(req):
    
    if req.user.is_authenticated:
        return redirect('home')
    
    if req.method == 'POST':
        username = req.POST.get('username').lower()
        password = req.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(req, 'User does not exist')
            
        user = authenticate(req, username=username, password=password)
        
        if user is not None:
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, 'Invalid username or password')
    
            
        
    return render(req, 'base/login_register.html', {'page': 'login'})

def register_user(req):
    form = UserCreationForm()
    
    if req.method == 'POST':
        form = UserCreationForm(req.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            user.username = user.username.lower()
            user.save()
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, 'An error occured during registration')
            
    return render(req, 'base/login_register.html', {'form': form})

def logout_user(req):
    logout(req)
    return redirect('home')