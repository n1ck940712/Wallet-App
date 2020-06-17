from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import entry
# Create your views here.

superuser = User.objects.filter(is_superuser=True)
if superuser.count() == 0:
    superuser=User.objects.create_user("admin","admin@admin.com","password")
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.save()

def index(request):
    if not request.user.is_authenticated:
        return render(request, "walletapp/login.html", {"message": "Login first"})
    context = {
    "user": request.user,
    "message": None
    }
    return render(request, "walletapp/index.html", context)

def signin(request):
    if request.method=="POST":
        email=request.POST.get("email")
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "walletapp/login.html", {"message":"Invalid Credentials"})
    return render(request, "walletapp/login.html", {"message":'message'})

def signout(request):
    logout(request)
    return render(request, "walletapp/login.html", {"message":"Successfully logged out."})
