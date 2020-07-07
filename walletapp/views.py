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
    if request.method == "GET":
        context = {
        "user": request.user,
        "category": dbCategory.objects.all(),
        "transaction": dbEntry.objects.order_by('-entryDate'),
        "transaction_date": dbEntry.objects.order_by('-entryDate').distinct('entryDate'),
        "accounts": dbAccount.objects.all(),
        "message": None,
        }
    elif request.method == "POST":
        filter_flag = False
        filter_type = request.POST.get('filterType')
        filter_category = request.POST.get('filterCategory')
        filter_note = request.POST.get('filterNote')
        filter_account = request.POST.get('filterAccount')
        filter_date_start = request.POST.get('filterDateStart')
        filter_date_end = request.POST.get('filterDateEnd')
        if filter_type != "" and filter_flag == True:
            transaction_result = transaction_result.filter(type=filter_type)
            filter_flag = True
        elif filter_type != "":
            transaction_result = dbEntry.objects.filter(type=filter_type)
            filter_flag = True
        if filter_category != "" and filter_flag == True:
            transaction_result = transaction_result.filter(category=filter_category)
            filter_flag = True
        elif filter_category !="":
            transaction_result = dbEntry.objects.filter(category=filter_category)
            filter_flag = True
        if filter_note != "" and filter_flag == True:
            transaction_result = transaction_result.filter(entryNote=filter_note)
            filter_flag = True
        elif filter_note != "":
            transaction_result = dbEntry.objects.filter(entryNote=filter_note)
            filter_flag = True
        if filter_account != "" and filter_flag == True:
            transaction_result = transaction_result.filter(fromAccount=filter_account)|transaction_result.filter(toAccount=filter_account)
            filter_flag = True
        elif filter_account != "":
            transaction_result = dbEntry.objects.filter(fromAccount=filter_account)|dbEntry.objects.filter(toAccount=filter_account)
            filter_flag = True
        # Date filtering
        if filter_date_end == filter_date_start and filter_date_start != "":
            if filter_flag == True:
                transaction_result = transaction_result.filter(entryDate=filter_date_start)
                filter_flag = True
            else:
                transaction_result = dbEntry.objects.filter(entryDate=filter_date_start)
                filter_flag = True
        elif filter_date_end != filter_date_start:
            if filter_flag == True:
                transaction_result = transaction_result.filter(entryDate__range=[filter_date_start, filter_date_end])
            else:
                transaction_result = dbEntry.objects.filter(entryDate__range=[filter_date_start, filter_date_end])
                filter_flag = True
        if filter_flag == False:
            transaction_result = dbEntry.objects.all()
        context = {
        "user": request.user,
        "category": dbCategory.objects.all(),
        "transaction": transaction_result.order_by('-entryDate'),
        "transaction_date": transaction_result.values('entryDate').distinct(),
        "accounts": dbAccount.objects.all(),
        "message": None,
        }
    return render(request, "walletapp/index.html", context)

def addEntry(request):
    if request.method == "POST":
        new_entry = dbEntry(amount=request.POST.get('new_entry_amount'), category=request.POST.get('new_entry_category'), fromAccount=request.POST.get('new_entry_from'), toAccount=request.POST.get('new_entry_to'), entryNote=request.POST.get('new_entry_note'), type=request.POST.get('new_entry_type'), entryDate=request.POST.get('new_entry_date'))
        new_entry.save()
    return HttpResponseRedirect(reverse("index"))

def deleteEntry(request):
    if request.method == "POST":
        del_entry = dbEntry.objects.get(pk=request.POST['entry_id'])
        del_entry.delete()
    return HttpResponseRedirect(reverse("index"))

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
    return HttpResponseRedirect(reverse("index"))

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
    return HttpResponseRedirect(reverse("settingPage"))

def editCategory(request):
    if request.method == "POST":
        edit_category = dbCategory.objects.get(pk=request.POST['category_id'])
        edit_category.category=request.POST['edit_category_input']
        edit_category.save()
    return HttpResponseRedirect(reverse("settingPage"))

def addCategory(request):
    if request.method == "POST":
        edit_category = dbCategory(category=request.POST['add_category_input'])
        edit_category.save()
    return HttpResponseRedirect(reverse("settingPage"))

def deleteAccount(request):
    if request.method == "POST":
        delete_account = dbAccount.objects.get(pk=request.POST['account_id'])
        delete_account.delete()
    return HttpResponseRedirect(reverse("settingPage"))

def editAccount(request):
    if request.method == "POST":
        edit_account = dbAccount.objects.get(pk=request.POST['account_id'])
        edit_account.accountName = request.POST['edit_account_name']
        edit_account.accountBalance = request.POST['edit_account_balance']
        edit_account.accountType = request.POST['edit_account_type']
        edit_account.save()
    return HttpResponseRedirect(reverse("settingPage"))

def addAccount(request):
    if request.method == "POST":
        edit_account = dbAccount(accountName = request.POST['add_account_name'], accountBalance = request.POST['add_account_balance'], accountType = request.POST['add_account_type'])
        edit_account.save()
    return HttpResponseRedirect(reverse("settingPage"))
