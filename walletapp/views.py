from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import dbEntry, dbCategory, dbAccount, dbAccountType
from django.core import serializers
from django.db.models import Sum
import json

#initialize superuser
superuser = User.objects.filter(is_superuser=True)
if superuser.count() == 0:
    superuser=User.objects.create_user("admin","admin@admin.com","password")
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.save()

# load pages
def index(request):
    if not request.user.is_authenticated:
        return render(request, "walletapp/login.html", {"message": "Login first"})
    context = {
    'user': request.user,
    'accounts': dbAccount.objects.all().order_by('accountName'),
    'category': dbCategory.objects.all().order_by('categoryName'),
    'transactions': dbEntry.objects.all()
    }
    return render(request, "walletapp/index.html", context)

def settings(request):
    context = {
    "user": request.user,
    "category": dbCategory.objects.all().order_by("categoryName"),
    "transaction": dbEntry.objects.all().reverse(),
    "accounts": dbAccount.objects.all().order_by("accountName"),
    "accountTypes": dbAccount.objects.distinct('accountType').order_by('accountType'),
    "message": None,
    }
    return render(request, "walletapp/settings.html", context)

def loadSettings(request):
    get_category = dbCategory.objects.all().order_by('categoryName')
    get_account = dbAccount.objects.all().order_by('accountName')
    data = {
        'account': serializers.serialize('json', get_account),
        'category': serializers.serialize('json', get_category),
    }
    return JsonResponse(data)

def overview(request):
    data = {
    # "user": request.user,
    "accounts": dbAccount.objects.all().order_by("accountName"),
    "message": None,
    }
    return render(request, "walletapp/overview.html", data)

def getAccountOverview(request): # overview graph

    selected_account = int(request.GET.get('selected_account'))
    filter_date_start = request.GET.get('filter_date_start')
    filter_date_end = request.GET.get('filter_date_end')
    filter_date_end_plus1 = request.GET.get('filter_date_end+1')

    if (filter_date_start and filter_date_end) == '' : #no date filter
        print('nodatefilter')
        filtered_transaction = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).order_by('-entryDate')
        filtered_expense_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(type="expense").values('category').annotate(total=Sum('amount'))
        filtered_income_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(type="income").values('category').annotate(total=Sum('amount'))
        balance_history = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).values('entryDate').annotate(total=Sum('amount')).order_by('entryDate')
        selected_account_balance = dbAccount.objects.get(pk=selected_account).accountBalance
    elif (filter_date_end != filter_date_start): #yes date filter
        filtered_transaction = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_start, filter_date_end]).order_by('-entryDate')
        filtered_expense_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_start, filter_date_end]).filter(type="expense").values('category').annotate(total=Sum('amount'))
        filtered_income_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_start, filter_date_end]).filter(type="income").values('category').annotate(total=Sum('amount'))
        balance_history = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_start, filter_date_end]).values('entryDate').annotate(total=Sum('amount')).order_by('entryDate')

        last_entry_date = dbEntry.objects.all().order_by('entryDate').last().entryDate ##get balance at filter end date
        get_balance_at_date = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_end_plus1, last_entry_date]).order_by('-entryDate')
        selected_account_balance = float(dbAccount.objects.get(pk=selected_account).accountBalance)
        print(get_balance_at_date)
        for item in get_balance_at_date:
            if (item.type == 'transfer') and (item.fromAccount == selected_account):
                selected_account_balance += float(item.amount)
            elif (item.type == 'transfer') and (item.toAccount == selected_account):
                selected_account_balance -= float(item.amount)
            else:
                selected_account_balance -= float(item.amount)


    total_change = float(0) ####total change calculation
    total_income = float(0)
    total_expense = float(0)
    total_transfer = float(0)
    daily_change_dict = []
    daily_change = {}
    first_run_flag=True
    for item in filtered_transaction:
        if first_run_flag==True:
            test_date = item.entryDate
            daily_total = float(0)
        if item.entryDate != test_date:
            daily_total = float(0)
        if item.type == "income":
            total_change += float(item.amount)
            total_income += float(item.amount)
            daily_total += float(item.amount)
        if item.type == "expense":
            total_change += float(item.amount)
            total_expense += float(item.amount)
            daily_total += float(item.amount)
        if item.type == "transfer":
            total_transfer += float(item.amount)
            if item.fromAccount.pk == selected_account:
                daily_total -= float(item.amount)
            if item.toAccount.pk == selected_account:
                daily_total += float(item.amount)
        if item.type == "system":
            daily_total += float(item.amount)
        daily_change[str(item.entryDate)] = daily_total
        test_date = item.entryDate
        first_run_flag=False
    data = {
    'category': serializers.serialize('json', dbCategory.objects.all().order_by('categoryName')),
    'daily_change': daily_change,
    "expense_category": list(filtered_expense_category),
    "income_category": list(filtered_income_category),
    # "balance_history": list(balance_history),
    "total_change": total_change,
    "total_income": total_income,
    "total_expense": total_expense,
    "total_transfer": total_transfer,
    "selected_account_balance": selected_account_balance,
    }
    return JsonResponse(data, content_type="application/json", safe=False)

# entry
def addEntry(request):
    if request.method == "POST":
        new_entry_type = request.POST.get('new_entry_type')
        new_entry_from = request.POST.get('new_entry_from')
        new_entry_to = request.POST.get('new_entry_to')
        new_entry_note = request.POST.get('new_entry_note')
        new_entry_date = request.POST.get('new_entry_date')
        new_entry_category = request.POST.get('new_entry_category')
        new_entry_amount = request.POST.get('new_entry_amount')
        if new_entry_type=="expense":
            get_account = dbAccount.objects.get(pk=new_entry_from)
            get_account.accountBalance=str(float(get_account.accountBalance)-float(new_entry_amount))
            get_account.save()
            new_entry_amount = str(float(new_entry_amount)*(-1))
            new_entry = dbEntry(amount=new_entry_amount, category=dbCategory.objects.get(pk=new_entry_category), fromAccount=dbAccount.objects.get(pk=new_entry_from), entryNote=new_entry_note, type=new_entry_type, entryDate=new_entry_date)
        if new_entry_type=="income":
            get_account = dbAccount.objects.get(pk=new_entry_to)
            get_account.accountBalance=str(float(get_account.accountBalance)+float(new_entry_amount))
            get_account.save()
            new_entry = dbEntry(amount=new_entry_amount, category=dbCategory.objects.get(pk=new_entry_category), toAccount=dbAccount.objects.get(new_entry_to), entryNote=new_entry_note, type=new_entry_type, entryDate=new_entry_date)
        if new_entry_type=="transfer":
            get_account_from = dbAccount.objects.get(pk=new_entry_from)
            get_account_to = dbAccount.objects.get(pk=new_entry_to)
            get_account_from.accountBalance=str(float(get_account_from.accountBalance)-float(new_entry_amount))
            get_account_to.accountBalance=str(float(get_account_to.accountBalance)+float(new_entry_amount))
            get_account_to.save()
            get_account_from.save()
            new_entry = dbEntry(amount=new_entry_amount, category=dbCategory.objects.get(pk=new_entry_category), fromAccount=dbAccount.objects.get(pk=new_entry_from), toAccount=dbAccount.objects.get(new_entry_to), entryNote=new_entry_note, type=new_entry_type, entryDate=new_entry_date)
        new_entry.save()

        data = {
        'message': 'New transaction added.'
        }
    return JsonResponse(data)

def editEntry(request):
    context = {
    # "user": request.user,
    "chosen_entry": serializers.serialize('json', dbEntry.objects.filter(pk=request.GET.get('entry_id'))),
    "category": serializers.serialize('json', dbCategory.objects.all().order_by("categoryName")),
    "accounts": serializers.serialize('json', dbAccount.objects.all().order_by("accountName")),
    }
    return JsonResponse(context)

def editEntryConfirm(request):
    if request.method == "POST":
        old_entry = dbEntry.objects.get(pk=request.POST['edit_entry_pk'])
        if old_entry.toAccount is not None:
            edit_entry_to = int(request.POST.get('edit_entry_to'))
        if old_entry.fromAccount is not None:
            edit_entry_from = int(request.POST.get('edit_entry_from'))
        if old_entry.category is not None:
            edit_entry_category = int(request.POST.get('edit_entry_category'))
        edit_entry_note= request.POST.get('edit_entry_note')
        edit_entry_amount = request.POST.get('edit_entry_amount')
        entry_change_flag = False
        if old_entry.amount != float(edit_entry_amount):
            print("amount change")
            if old_entry.type == "expense":
                get_account = old_entry.fromAccount
                amount_diff = float(edit_entry_amount)-float(old_entry.amount)
                get_account.accountBalance = str(float(get_account.accountBalance)+amount_diff)
                get_account.save()
            if old_entry.type == "income":
                get_account = old_entry.toAccount
                amount_diff = float(edit_entry_amount)-float(old_entry.amount)
                get_account.accountBalance = str(float(get_account.accountBalance)+amount_diff)
                get_account.save()
            if old_entry.type == "transfer":
                get_account_from = old_entry.fromAccount
                get_account_to = old_entry.toAccount
                amount_diff = float(edit_entry_amount)-float(old_entry.amount)
                get_account_from.accountBalance = str(float(get_account_from.accountBalance) - amount_diff)
                get_account_to.accountBalance = str(float(get_account_to.accountBalance) + amount_diff)
                get_account_from.save()
                get_account_to.save()
            old_entry.amount = edit_entry_amount
            entry_change_flag = True
        if old_entry.category is not None:
            if old_entry.category.pk != edit_entry_category:
                entry_change_flag = True
                print("category change")
                old_entry.category = dbCategory.objects.get(pk=edit_entry_category)
        if old_entry.fromAccount is not None:
            if old_entry.fromAccount.pk != edit_entry_from:
                print("from account change")
                if old_entry.type == "expense":
                    get_account_ori = old_entry.fromAccount
                    get_account_new = dbAccount.objects.get(pk=edit_entry_from)
                    get_account_ori.accountBalance = str(float(get_account_ori.accountBalance) - float(edit_entry_amount))
                    get_account_new.accountBalance = str(float(get_account_new.accountBalance) + float(edit_entry_amount))
                    get_account_ori.save()
                    get_account_new.save()
                if old_entry.type == "transfer":
                    get_account_ori = dbAccount.objects.get(pk=old_entry.fromAccount.pk)
                    get_account_new = dbAccount.objects.get(pk=edit_entry_from)
                    get_account_ori.accountBalance = str(float(get_account_ori.accountBalance) + float(edit_entry_amount))
                    get_account_new.accountBalance = str(float(get_account_new.accountBalance) - float(edit_entry_amount))
                    get_account_ori.save()
                    get_account_new.save()
                old_entry.fromAccount = dbAccount.objects.get(pk=edit_entry_from)
                entry_change_flag = True
        if old_entry.toAccount is not None:
            if old_entry.toAccount.pk != edit_entry_to:
                print("to account change")
                if old_entry.type == "income":
                    get_account_ori = old_entry.toAccount
                    get_account_new = dbAccount.objects.get(pk=edit_entry_to)
                    get_account_ori.accountBalance = str(float(get_account_ori.accountBalance) - float(edit_entry_amount))
                    get_account_new.accountBalance = str(float(get_account_new.accountBalance) + float(edit_entry_amount))
                    get_account_ori.save()
                    get_account_new.save()
                if old_entry.type == "transfer":
                    get_account_ori = dbAccount.objects.get(pk=old_entry.toAccount.pk)
                    get_account_new = dbAccount.objects.get(pk=edit_entry_to)
                    get_account_ori.accountBalance = str(float(get_account_ori.accountBalance) - float(edit_entry_amount))
                    get_account_new.accountBalance = str(float(get_account_new.accountBalance) + float(edit_entry_amount))
                    get_account_ori.save()
                    get_account_new.save()
                old_entry.toAccount = dbAccount.objects.get(pk=edit_entry_to)
                entry_change_flag = True
        if old_entry.entryNote != edit_entry_note:
            print("note change")
            old_entry.entryNote = edit_entry_note
            entry_change_flag = True
        old_entry.save()
    data = {
    'entry_change_flag': entry_change_flag,
    }
    return JsonResponse(data)

def deleteEntry(request):
    del_entry = dbEntry.objects.get(pk=request.GET.get('entry_id'))
    if del_entry.type=="expense":
        get_account = dbAccount.objects.get(pk=del_entry.fromAccount.pk)
        get_account.accountBalance=str(float(get_account.accountBalance)-float(del_entry.amount))
        get_account.save()
    if del_entry.type=="income":
        get_account = dbAccount.objects.get(pk=del_entry.toAccount.pk)
        get_account.accountBalance=str(float(get_account.accountBalance)-float(del_entry.amount))
        get_account.save()
    if del_entry.type=="System":
        get_account = dbAccount.objects.get(pk=del_entry.toAccount.pk)
        get_account.accountBalance=str(float(get_account.accountBalance)-float(del_entry.amount))
        get_account.save()
    if del_entry.type=="transfer":
        get_account_from = dbAccount.objects.get(pk=del_entry.fromAccount.pk)
        get_account_to = dbAccount.objects.get(pk=del_entry.toAccount.pk)
        get_account_from.accountBalance=str(float(get_account_from.accountBalance)+float(del_entry.amount))
        get_account_to.accountBalance=str(float(get_account_to.accountBalance)-float(del_entry.amount))
        get_account_to.save()
        get_account_from.save()
    del_entry.delete()
    data = {
        'message': 'Transaction deleted'
    }
    return JsonResponse(data)

def loadEntry(request):
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
    "category": serializers.serialize('json', dbCategory.objects.all().order_by("categoryName")),
    "transaction": serializers.serialize('json', transaction_result.order_by('-entryDate')),
    "transaction_date": serializers.serialize('json', transaction_result.order_by('-entryDate').distinct('entryDate')),
    "accounts": serializers.serialize('json', dbAccount.objects.all().order_by("accountName")),
    "message": None,
    }
    return JsonResponse(data)

# category
def addCategory(request):
    new_category_name = request.POST.get('new_category_name')
    new_category_type = request.POST.get('new_category_type')
    if dbCategory.objects.filter(categoryName=new_category_name, categoryType=new_category_type).exists():
        data = {
            'message': 'Another category with the same name. Add category failed.'
        }
    elif request.method == "POST":
        edit_category = dbCategory(categoryName=new_category_name, categoryType=new_category_type)
        edit_category.save()
        data = {
            'message': 'add category success'
        }
    return JsonResponse(data)

def editCategory(request):
    if request.method == "POST":
        edit_category = dbCategory.objects.get(pk=request.GET.get('category_id'))
        edit_category.categoryName=request.GET.get('edit_category_input')
        edit_category.save()
    data = {
        'message': 'edit category success',
    }
    return JsonResponse(data)

def deleteCategory(request):
    delete_category = dbCategory.objects.get(pk=request.GET.get('category_id'))
    delete_category.delete()
    data = {
        'message': 'delete category successful',
    }
    return JsonResponse(data)

# account
def addAccount(request):
    if request.method == "POST":
        edit_account = dbAccount(accountName = request.POST['add_account_name'], accountBalance = request.POST['add_account_balance'], accountType = request.POST['add_account_type'])
        edit_account.save()
        account_first_entry = dbEntry(amount=request.POST.get('add_account_balance'), fromAccount=edit_account, toAccount=edit_account, entryNote='new account', type='system')
        account_first_entry.save()
    data = {
        'message': 'add account successful'
    }
    return JsonResponse(data)

def editAccount(request):
    if request.method == "POST":
        edit_account = dbAccount.objects.get(pk=request.POST['account_id'])
        edit_account_balance = request.POST.get('edit_account_balance')
        edit_account_name = request.POST.get('edit_account_name')
        if edit_account.accountBalance != edit_account_balance:
            balanceDiff = float(edit_account_balance) - float(edit_account.accountBalance)
            balanceDiffEntry = dbEntry(amount=balanceDiff, fromAccount=edit_account, toAccount=edit_account, entryNote='edit balance', type='system')
            balanceDiffEntry.save()
        edit_account.accountName = edit_account_name
        edit_account.accountBalance = edit_account_balance
        edit_account.accountType = request.POST.get('edit_account_type')
        edit_account.save()
    data = {
        'message': 'edit account success'
    }
    return JsonResponse(data)

def deleteAccount(request):
    if request.method == "POST":
        delete_account = dbAccount.objects.get(pk=request.POST['account_id'])
        delete_account.delete()
    data = {
        'message': 'delete account successful'
    }
    return JsonResponse(data)

# signin signout
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
