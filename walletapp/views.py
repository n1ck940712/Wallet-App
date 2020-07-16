from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import dbEntry, dbCategory, dbAccount, dbAccountType
from django.core import serializers
from django.db.models import Sum
import json

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
    'user': request.user,
    }
    return render(request, "walletapp/index.html", context)

def filterTransaction(request):
    filter_flag = False
    filter_type = request.GET.get('filterType')
    filter_category = request.GET.get('filterCategory')
    filter_note = request.GET.get('filterNote')
    filter_account = request.GET.get('filterAccount')
    filter_date_start = request.GET.get('filterDateStart')
    filter_date_end = request.GET.get('filterDateEnd')
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
    data = {
    # "user": list(request.user),
    "category": serializers.serialize('json', dbCategory.objects.all().order_by("category")),
    "transaction": serializers.serialize('json', transaction_result.order_by('-entryDate')),
    "transaction_date": serializers.serialize('json', transaction_result.order_by('-entryDate').distinct('entryDate')),
    "accounts": serializers.serialize('json', dbAccount.objects.all().order_by("accountName")),
    "message": None,
    }
    return JsonResponse(data)

def overview(request):
    if request.method=="GET":
        filtered_transaction = dbEntry.objects.all().order_by('-entryDate')
    if request.method=="POST":
        selected_account = request.POST.get('filterAccount')
        filter_date_start = request.POST.get('filterDateStart')
        filter_date_end = request.POST.get('filterDateEnd')
        filtered_transaction = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).order_by('-entryDate')
        filtered_transaction = filtered_transaction.filter(entryDate__range=[filter_date_start, filter_date_end])

    total_change = float(0) ####total change calculation
    total_income = float(0)
    total_expense = float(0)
    total_transfer = float(0)
    for item in filtered_transaction:
        if item.type == "Income":
            total_change += float(item.amount)
            total_income += float(item.amount)
        if item.type == "Expense":
            total_change -= float(item.amount)
            total_expense += float(item.amount)
        if item.type == "Transfer":
            total_transfer += float(item.amount)

    context = {
    "user": request.user,
    "accounts": dbAccount.objects.all().order_by("accountName"),
    "transaction": filtered_transaction,
    "total_change": total_change,
    "total_income": total_income,
    "total_expense": total_expense,
    "total_transfer": total_transfer,
    "message": None,
    }
    return render(request, "walletapp/overview.html", context)

# testing ajax requests
def overviewAjax(request):
    selected_account = request.GET.get('selected_account')
    filtered_transaction = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).order_by('-entryDate')
    filtered_transaction_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(type="Expense").values('category').annotate(total=Sum('amount'))
    balance_history = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).values('entryDate').annotate(total=Sum('amount'))
    selected_account_balance = dbAccount.objects.filter(accountName=selected_account)

    total_change = float(0) ####total change calculation
    total_income = float(0)
    total_expense = float(0)
    total_transfer = float(0)
    for item in filtered_transaction:
        if item.type == "Income":
            total_change += float(item.amount)
            total_income += float(item.amount)
        if item.type == "Expense":
            total_change -= float(item.amount)
            total_expense += float(item.amount)
        if item.type == "Transfer":
            total_transfer += float(item.amount)
    context = {
    "transaction": serializers.serialize("json", filtered_transaction),
    "transaction_category": list(filtered_transaction_category),
    "balance_history": list(balance_history),
    "total_change": total_change,
    "total_income": total_income,
    "total_expense": total_expense,
    "total_transfer": total_transfer,
    "selected_account_balance": serializers.serialize("json", selected_account_balance),
    }
    return JsonResponse(context, content_type="application/json", safe=False)

def addEntry(request):
    if request.method == "POST":
        new_entry_type = request.POST.get('new_entry_type')
        new_entry_from = request.POST.get('new_entry_from')
        new_entry_to = request.POST.get('new_entry_to')
        new_entry_note = request.POST.get('new_entry_note')
        new_entry_date = request.POST.get('new_entry_date')
        new_entry_category = request.POST.get('new_entry_category')
        new_entry_amount = request.POST.get('new_entry_amount')
        if new_entry_type=="Expense":
            get_account = dbAccount.objects.get(accountName=new_entry_from)
            get_account.accountBalance=str(float(get_account.accountBalance)-float(new_entry_amount))
            get_account.save()
        if new_entry_type=="Income":
            get_account = dbAccount.objects.get(accountName=new_entry_to)
            get_account.accountBalance=str(float(get_account.accountBalance)+float(new_entry_amount))
            get_account.save()
        if new_entry_type=="Transfer":
            get_account_from = dbAccount.objects.get(accountName=new_entry_from)
            get_account_to = dbAccount.objects.get(accountName=new_entry_to)
            get_account_from.accountBalance=str(float(get_account_from.accountBalance)-float(new_entry_amount))
            get_account_to.accountBalance=str(float(get_account_to.accountBalance)+float(new_entry_amount))
            get_account_to.save()
            get_account_from.save()
        new_entry = dbEntry(amount=new_entry_amount, category=new_entry_category, fromAccount=new_entry_from, toAccount=new_entry_to, entryNote=new_entry_note, type=new_entry_type, entryDate=new_entry_date)
        new_entry.save()
    return HttpResponseRedirect(reverse("index"))

def deleteEntry(request):
    if request.method == "POST":
        del_entry = dbEntry.objects.get(pk=request.POST['entry_id'])
        if del_entry.type=="Expense":
            get_account = dbAccount.objects.get(accountName=del_entry.fromAccount)
            get_account.accountBalance=str(float(get_account.accountBalance)+float(del_entry.amount))
            get_account.save()
        if del_entry.type=="Income":
            get_account = dbAccount.objects.get(accountName=del_entry.toAccount)
            get_account.accountBalance=str(float(get_account.accountBalance)-float(del_entry.amount))
            get_account.save()
        if del_entry.type=="Transfer":
            get_account_from = dbAccount.objects.get(accountName=del_entry.fromAccount)
            get_account_to = dbAccount.objects.get(accountName=del_entry.toAccount)
            get_account_from.accountBalance=str(float(get_account_from.accountBalance)+float(del_entry.amount))
            get_account_to.accountBalance=str(float(get_account_to.accountBalance)-float(del_entry.amount))
            get_account_to.save()
            get_account_from.save()
        del_entry.delete()
    return HttpResponseRedirect(reverse("index"))

def editEntry(request):
    if request.method == "POST":
        context = {
        "user": request.user,
        "chosen_entry": dbEntry.objects.get(pk=request.POST['entry_id']),
        "category": dbCategory.objects.all().order_by("category"),
        "accounts": dbAccount.objects.all().order_by("accountName"),
        }
    return render(request, "walletapp/edit.html", context)

def editEntryConfirm(request):
    if request.method == "POST":
        edit_entry_amount = request.POST.get('edit_entry_amount')
        edit_entry_category = request.POST.get('edit_entry_category')
        edit_entry_from = request.POST.get('edit_entry_from')
        edit_entry_to = request.POST.get('edit_entry_to')
        edit_entry_note= request.POST.get('edit_entry_note')
        old_entry = dbEntry.objects.get(pk=request.POST['entry_id'])
        if old_entry.amount != float(edit_entry_amount):
            print("amount change")
            if old_entry.type == "Expense":
                get_account = dbAccount.objects.get(accountName=old_entry.fromAccount)
                amount_diff = float(edit_entry_amount)-float(old_entry.amount)
                get_account.accountBalance = str(float(get_account.accountBalance)-amount_diff)
                get_account.save()
            if old_entry.type == "Income":
                get_account = dbAccount.objects.get(accountName=old_entry.toAccount)
                amount_diff = float(edit_entry_amount)-float(old_entry.amount)
                get_account.accountBalance = str(float(get_account.accountBalance)+amount_diff)
                get_account.save()
            if old_entry.type == "Transfer":
                get_account_from = dbAccount.objects.get(accountName=old_entry.fromAccount)
                get_account_to = dbAccount.objects.get(accountName=old_entry.toAccount)
                amount_diff = float(edit_entry_amount)-float(old_entry.amount)
                get_account_from.accountBalance = str(float(get_account_from.accountBalance) - amount_diff)
                get_account_to.accountBalance = str(float(get_account_to.accountBalance) + amount_diff)
                get_account_from.save()
                get_account_to.save()
            old_entry.amount = edit_entry_amount
        if old_entry.category != edit_entry_category:
            print("category change")
            old_entry.category = edit_entry_category
        if old_entry.fromAccount != edit_entry_from:
            print("from account change")
            if old_entry.type == "Expense":
                get_account_ori = dbAccount.objects.get(accountName=old_entry.fromAccount)
                get_account_new = dbAccount.objects.get(accountName=edit_entry_from)
                get_account_ori.accountBalance = str(float(get_account_ori.accountBalance) + float(edit_entry_amount))
                get_account_new.accountBalance = str(float(get_account_new.accountBalance) - float(edit_entry_amount))
                get_account_ori.save()
                get_account_new.save()
            old_entry.fromAccount = edit_entry_from
            if old_entry.type == "Transfer":
                get_account_ori = dbAccount.objects.get(accountName=old_entry.fromAccount)
                get_account_new = dbAccount.objects.get(accountName=edit_entry_from)
                get_account_ori.accountBalance = str(float(get_account_ori.accountBalance) + float(edit_entry_amount))
                get_account_new.accountBalance = str(float(get_account_new.accountBalance) - float(edit_entry_amount))
                get_account_ori.save()
                get_account_new.save()
            old_entry.fromAccount = edit_entry_from
        if old_entry.toAccount != edit_entry_to:
            print(old_entry.toAccount)
            print(edit_entry_to)
            print("to account change")
            if old_entry.type == "Income":
                get_account_ori = dbAccount.objects.get(accountName=old_entry.fromAccount)
                get_account_new = dbAccount.objects.get(accountName=edit_entry_to)
                get_account_ori.accountBalance = str(float(get_account_ori.accountBalance) - float(edit_entry_amount))
                get_account_new.accountBalance = str(float(get_account_new.accountBalance) + float(edit_entry_amount))
                get_account_ori.save()
                get_account_new.save()
            if old_entry.type == "Transfer":
                get_account_ori = dbAccount.objects.get(accountName=old_entry.toAccount)
                get_account_new = dbAccount.objects.get(accountName=edit_entry_to)
                get_account_ori.accountBalance = str(float(get_account_ori.accountBalance) - float(edit_entry_amount))
                get_account_new.accountBalance = str(float(get_account_new.accountBalance) + float(edit_entry_amount))
                get_account_ori.save()
                get_account_new.save()
            old_entry.toAccount = edit_entry_to
        if old_entry.entryNote != edit_entry_note:
            print("note change")
            old_entry.entryNote = edit_entry_note
        old_entry.save()
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
    "category": dbCategory.objects.all().order_by("category"),
    "transaction": dbEntry.objects.all().reverse(),
    "accounts": dbAccount.objects.all().order_by("accountName"),
    "accountTypes": dbAccount.objects.distinct('accountType').order_by('accountType'),
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
