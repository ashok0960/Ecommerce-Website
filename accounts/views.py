from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import *
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def userRegister(request):
    if request.method == 'POST':
        user = UserCreationForm(request.POST)
        if user.is_valid():
            user.save()
            messages.success(request,'User Created Successfully.')
            return redirect('login')
        else:
            messages.error(request,'Invalid Username or Password.')
            return render(request,'auth/register.html',{'form':user})
    context = {
        'form': UserCreationForm
    }
    return render(request,'auth/register.html',context)


def userLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request,user)
            if user.is_superuser:
                messages.success(request, f"Welcome {user.username}!")
                return redirect('admin-dashboard')
            elif user.is_staff:
                messages.success(request, f"Welcome {user.username}!")
                return redirect('vendor-dashboard')
            else:
                messages.success(request, f"Welcome {user.username}!")
                return redirect('home')
        else:
            messages.error(request,'User not Found!')
            return render(request,'auth/login.html',{'form':LoginForm})

    context={
        'form': LoginForm
    }
    return render(request,'auth/login.html',context)


def userLogout(request):
    logout(request)
    messages.success(request,"User Logout Success!")
    return redirect('/')