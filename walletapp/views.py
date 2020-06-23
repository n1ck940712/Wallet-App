from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import dbEntry, dbCategory, dbAccount, dbAccountType
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
    "category": dbCategory.objects.all(),
    "transaction": dbEntry.objects.all().reverse(),
    "accounts": dbAccount.objects.all(),
    "message": None,
    }
    return render(request, "walletapp/index.html", context)

def addEntry(request):
    if request.method == "POST":
        new_entry = dbEntry(amount=request.POST['new_entry_amount'], category=request.POST['new_entry_category'], fromAccount=request.POST['new_entry_from'], toAccount=request.POST['new_entry_to'])
        new_entry.save()
    context = {
    "user": request.user,
    "category": dbCategory.objects.all(),
    "transaction": dbEntry.objects.all().reverse(),
    "accounts": dbAccount.objects.all(),
    "message": None,
    }
    return render(request, "walletapp/index.html", context)

def deleteEntry(request):
    if request.method == "POST":
        del_entry = dbEntry.objects.get(pk=request.POST['entry_id'])
        del_entry.delete()
    context = {
    "user": request.user,
    "category": dbCategory.objects.all(),
    "transaction": dbEntry.objects.all().reverse(),
    "accounts": dbAccount.objects.all(),
    "message": None,
    }
    return render(request, "walletapp/index.html", context)

def editEntry(request):
    if request.method == "POST":
        context = {
        "user": request.user,
        "chosen_entry": dbEntry.objects.get(pk=request.POST['entry_id'])
        }
    return render(request, "walletapp/edit.html", context)

def editEntryConfirm(request):
    if request.method == "POST":
        edit_entry = dbEntry.objects.get(pk=request.POST['entry_id'])
        edit_entry.amount = request.POST['edit_entry_amount']
        edit_entry.category = request.POST['edit_entry_category']
        edit_entry.fromAccount = request.POST['edit_entry_from']
        edit_entry.toAccount = request.POST['edit_entry_to']
        edit_entry.save()
        context = {
        "user": request.user,
        "category": dbCategory.objects.all(),
        "transaction": dbEntry.objects.all().reverse(),
        "accounts": dbAccount.objects.all(),
        "message": None,
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

def settingPage(request):
    context = {
    "user": request.user,
    "category": dbCategory.objects.all(),
    "transaction": dbEntry.objects.all().reverse(),
    "accounts": dbAccount.objects.all(),
    "message": None,
    }
    return render(request, "walletapp/setting.html", context)

def deleteCategory(request):
    if request.method == "POST":
        delete_category = dbCategory.objects.get(pk=request.POST['category_id'])
        delete_category.delete()
        context = {
        "user": request.user,
        "category": dbCategory.objects.all(),
        "transaction": dbEntry.objects.all().reverse(),
        "accounts": dbAccount.objects.all(),
        "message": None,
        }
    return render(request, "walletapp/setting.html", context)

def editCategory(request):
    if request.method == "POST":
        edit_category = dbCategory.objects.get(pk=request.POST['category_id'])
        edit_category.category=request.POST['edit_category_input']
        edit_category.save()
        context = {
        "user": request.user,
        "category": dbCategory.objects.all(),
        "transaction": dbEntry.objects.all().reverse(),
        "accounts": dbAccount.objects.all(),
        "message": None,
        }
    return render(request, "walletapp/setting.html", context)

def deleteAccount(request):
    if request.method == "POST":
        delete_account = dbAccount.objects.get(pk=request.POST['account_id'])
        delete_account.delete()
        context = {
        "user": request.user,
        "category": dbCategory.objects.all(),
        "transaction": dbEntry.objects.all().reverse(),
        "accounts": dbAccount.objects.all(),
        "message": None,
        }
    return render(request, "walletapp/setting.html", context)

def editAccount(request):
    if request.method == "POST":
        edit_account = dbAccount.objects.get(pk=request.POST['account_id'])
        edit_account.accountName = request.POST['edit_account_name']
        edit_account.accountBalance = request.POST['edit_account_balance']
        edit_account.accountType = request.POST['edit_account_type']
        edit_account.save()
        context = {
        "user": request.user,
        "category": dbCategory.objects.all(),
        "transaction": dbEntry.objects.all().reverse(),
        "accounts": dbAccount.objects.all(),
        "message": None,
        }
    return render(request, "walletapp/setting.html", context)
