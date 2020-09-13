from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import dbEntry, dbCategory, dbAccount, dbAccountType, MyUser
from django.core import serializers
from django.db.models import Sum
from datetime import datetime, timedelta
import json

# initialize superuser
superuser = MyUser.objects.filter(is_admin=True)
if superuser.count() == 0:
    superuser=MyUser.objects.create_user("admin","admin@admin.com","password")
    superuser.is_admin = True
    superuser.save()

# load pages
def index(request):
    if not request.user.is_authenticated:
        data = {
            'message': 'Login first.',
            'message_type': 'danger',
        }
        return redirect("signinfirst")
    data = {
    'user': request.user,
    'accounts': dbAccount.objects.filter(accountUser=request.user,is_active=True).order_by('accountName'),
    'expense_category': dbCategory.objects.filter(categoryUser=request.user, categoryType='expense').order_by('categoryName'),
    'income_category': dbCategory.objects.filter(categoryUser=request.user, categoryType='income').order_by('categoryName')
    }
    return render(request, "walletapp/index.html", data)

def settings(request):
    context = {
    "user": request.user,
    "accountTypes": dbAccountType.objects.all(),
    "message": None,
    }
    return render(request, "walletapp/settings.html", context)

def loadSettings(request):
    get_category = dbCategory.objects.filter(categoryUser=request.user, is_active=True).order_by('categoryName')
    get_account = dbAccount.objects.filter(accountUser=request.user, is_active=True).order_by('accountName')
    data = {
        'account': serializers.serialize('json', get_account),
        'category': serializers.serialize('json', get_category),
    }
    return JsonResponse(data)

def overview(request):
    get_account = dbAccount.objects.filter(accountUser=request.user).order_by('accountName')
    data = {
    # "user": request.user,
    "accounts": get_account,
    "message": None,
    }
    return render(request, "walletapp/overview.html", data)

def getAccountOverview(request): # overview graph
    selected_account = int(request.GET.get('selected_account'))
    filter_date_start = request.GET.get('filter_date_start')
    filter_date_end = request.GET.get('filter_date_end')
    filter_date_end_plus1 = str((datetime.strptime(filter_date_end,'%Y-%m-%d') + timedelta(days=1)).date())

    if (filter_date_start and filter_date_end) == '' : #no date filter
        filtered_transaction = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).order_by('-entryDate')
        filtered_expense_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(type="expense").values('category').annotate(total=Sum('amount'))
        filtered_income_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(type="income").values('category').annotate(total=Sum('amount'))
        selected_account_balance = float(dbAccount.objects.get(pk=selected_account).accountBalance)

    elif (filter_date_end != filter_date_start): #yes date filter
        filtered_transaction = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_start, filter_date_end]).order_by('-entryDate')
        filtered_expense_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_start, filter_date_end]).filter(type="expense").values('category').annotate(total=Sum('amount'))
        filtered_income_category = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_start, filter_date_end]).filter(type="income").values('category').annotate(total=Sum('amount'))

        last_entry_date = dbEntry.objects.all().order_by('entryDate').last().entryDate ##get balance at filter end date
        get_balance_at_date = (dbEntry.objects.filter(toAccount=selected_account) | dbEntry.objects.filter(fromAccount=selected_account)).filter(entryDate__range=[filter_date_end_plus1, last_entry_date]).order_by('-entryDate')
        selected_account_balance = float(dbAccount.objects.get(pk=selected_account).accountBalance)
        
        selected_account_full = dbAccount.objects.get(pk=selected_account)
        for item in get_balance_at_date:
            if (item.type == 'transfer') and (item.fromAccount == selected_account_full):
                selected_account_balance += float(item.amount)
            elif (item.type == 'transfer') and (item.toAccount == selected_account_full):
                selected_account_balance -= float(item.amount)
            else:
                selected_account_balance -= float(item.amount)

    total_change = float(0) ####total change calculation
    total_income = float(0)
    total_expense = float(0)
    total_transfer = float(0)
    first_run_flag=True
    daily_balance = {}
    count=0
    loop=1
    for item in filtered_transaction:
        if first_run_flag==True:
            test_date = item.entryDate
            daily_total = float(0)
        if item.entryDate != test_date:
            daily_balance[count]={'date':test_date,'change':daily_total}
            count+=1
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
            try:
                if item.fromAccount.pk == selected_account:
                    daily_total -= float(item.amount)
            except:
                pass
            try:
                if item.toAccount.pk == selected_account:
                    daily_total += float(item.amount)
            except:
                pass
        if item.type == "system":
            daily_total += float(item.amount)
        if loop == len(filtered_transaction):
            daily_balance[count]={'date':item.entryDate,'change':daily_total}
        test_date = item.entryDate
        first_run_flag=False
        loop+=1
    print(daily_balance)
    daily_balance2={}
    selected_account_balance2=selected_account_balance
    count=0
    global filter_date_start_flag
    filter_date_start_flag=False
    for i in daily_balance:
        date_minus_1 = str(daily_balance[i]['date']-timedelta(days=1))
        if str(daily_balance[i]['date'])!=filter_date_start:
            if count==0:
                daily_balance2[count]={'date':daily_balance[i]['date'],'balance':selected_account_balance2}
                count+=1
                selected_account_balance2-=daily_balance[i]['change']
                daily_balance2[count]={'date':date_minus_1,'balance':selected_account_balance2}
                count+=1
            else:
                daily_balance2[count]={'date':daily_balance[i]['date'],'balance':selected_account_balance2}
                count+=1
                selected_account_balance2-=daily_balance[i]['change']
                daily_balance2[count]={'date':date_minus_1,'balance':selected_account_balance2}
                count+=1
        else:
            daily_balance2[count]={'date':daily_balance[i]['date'],'balance':selected_account_balance2}
            count+=1
            filter_date_start_flag = True
    if not filter_date_start_flag:
        daily_balance2[count]={'date':filter_date_start,'balance':selected_account_balance2}

        
    data = {
    'category': serializers.serialize('json', dbCategory.objects.filter(categoryUser=request.user).order_by('categoryName')),
    'daily_change': daily_balance2,
    "expense_category": list(filtered_expense_category),
    "income_category": list(filtered_income_category),
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
        new_entry_note = request.POST.get('new_entry_note').lower()
        new_entry_date = request.POST.get('new_entry_date')
        new_entry_category = request.POST.get('new_entry_category')
        new_entry_amount = request.POST.get('new_entry_amount')
        if new_entry_type=="expense":
            get_account = dbAccount.objects.get(pk=new_entry_from)
            get_account.accountBalance=str(float(get_account.accountBalance)-float(new_entry_amount))
            get_account.save()
            new_entry_amount = str(float(new_entry_amount)*(-1))
            new_entry = dbEntry(entryUser=request.user, amount=new_entry_amount, category=dbCategory.objects.get(pk=new_entry_category), fromAccount=dbAccount.objects.get(pk=new_entry_from), entryNote=new_entry_note, type=new_entry_type, entryDate=new_entry_date)
        if new_entry_type=="income":
            get_account = dbAccount.objects.get(pk=new_entry_to)
            get_account.accountBalance=str(float(get_account.accountBalance)+float(new_entry_amount))
            get_account.save()
            new_entry = dbEntry(entryUser=request.user, amount=new_entry_amount, category=dbCategory.objects.get(pk=new_entry_category), toAccount=dbAccount.objects.get(pk=new_entry_to), entryNote=new_entry_note, type=new_entry_type, entryDate=new_entry_date)
        if new_entry_type=="transfer":
            get_account_from = dbAccount.objects.get(pk=new_entry_from)
            get_account_to = dbAccount.objects.get(pk=new_entry_to)
            get_account_from.accountBalance=str(float(get_account_from.accountBalance)-float(new_entry_amount))
            get_account_to.accountBalance=str(float(get_account_to.accountBalance)+float(new_entry_amount))
            get_account_to.save()
            get_account_from.save()
            new_entry = dbEntry(entryUser=request.user, amount=new_entry_amount, fromAccount=dbAccount.objects.get(pk=new_entry_from), toAccount=dbAccount.objects.get(pk=new_entry_to), entryNote=new_entry_note, type=new_entry_type, entryDate=new_entry_date)
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
        edit_entry_note= request.POST.get('edit_entry_note').lower()
        edit_entry_date= request.POST.get('edit_entry_date')
        edit_entry_amount = request.POST.get('edit_entry_amount')
        entry_change_flag = False
        if old_entry.amount != float(edit_entry_amount):
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
                old_entry.category = dbCategory.objects.get(pk=edit_entry_category)
        if old_entry.fromAccount is not None:
            if old_entry.fromAccount.pk != edit_entry_from:
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
            old_entry.entryNote = edit_entry_note
            entry_change_flag = True
        if old_entry.entryDate != edit_entry_date:
            old_entry.entryDate = edit_entry_date
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
        try:
            get_account_from = dbAccount.objects.get(pk=del_entry.fromAccount.pk)
            get_account_from.accountBalance=str(float(get_account_from.accountBalance)+float(del_entry.amount))
            get_account_from.save()
        except:
            pass
        try:
            get_account_to = dbAccount.objects.get(pk=del_entry.toAccount.pk)
            get_account_to.accountBalance=str(float(get_account_to.accountBalance)-float(del_entry.amount))
            get_account_to.save()
        except:
            pass
    del_entry.delete()
    data = {
        'message': 'Transaction deleted'
    }
    return JsonResponse(data)

def loadEntry(request):
    filter_type = request.GET.get('filterType')
    filter_category = request.GET.get('filterCategory')
    filter_note = request.GET.get('filterNote').lower()
    filter_account = request.GET.get('filterAccount')
    filter_date_start = request.GET.get('filterDateStart')
    filter_date_end = request.GET.get('filterDateEnd')
    transaction_result = dbEntry.objects.filter(entryUser=request.user)
    if filter_type != "":
        transaction_result = transaction_result.filter(type=filter_type)
    if filter_category != "":
        transaction_result = transaction_result.filter(category=filter_category)
    if filter_note != "":
        transaction_result = transaction_result.filter(entryNote=filter_note)
    if filter_account != "":
        transaction_result = transaction_result.filter(fromAccount=filter_account)|transaction_result.filter(toAccount=filter_account)
    # Date filtering
    if filter_date_end == filter_date_start and filter_date_start != "":
        transaction_result = transaction_result.filter(entryDate=filter_date_start)
    elif filter_date_end != filter_date_start:
        transaction_result = transaction_result.filter(entryDate__range=[filter_date_start, filter_date_end])
    data = {
    "category": serializers.serialize('json', dbCategory.objects.all().order_by("categoryName")),
    "transaction": serializers.serialize('json', transaction_result.order_by('-entryDate')),
    "transaction_date": serializers.serialize('json', transaction_result.order_by('-entryDate').distinct('entryDate')),
    'transaction_category': serializers.serialize('json', transaction_result.distinct('category')),
    "accounts": serializers.serialize('json', dbAccount.objects.filter(accountUser=request.user,is_active=True).order_by("accountName")),
    "message": None,
    }
    return JsonResponse(data)

# category
def addCategory(request):
    new_category_name = request.POST.get('new_category_name').lower()
    new_category_type = request.POST.get('new_category_type')
    if dbCategory.objects.filter(categoryUser=request.user, categoryName=new_category_name, categoryType=new_category_type).exists():
        data = {
            'message': 'Another category with the same name. Add category failed.',
            'message_type': 'danger'
        }
    elif request.method == "POST":
        edit_category = dbCategory(categoryUser=request.user, categoryName=new_category_name, categoryType=new_category_type)
        edit_category.save()
        data = {
            'message': 'add category success',
            'message_type': 'success'
        }
    return JsonResponse(data)

def editCategory(request):
    if request.method == "POST":
        edit_category = dbCategory.objects.get(pk=request.POST.get('category_id'))
        edit_category.categoryName=request.POST.get('edit_category_input').lower()
        edit_category.save()
    data = {
        'message': 'edit category success',
    }
    return JsonResponse(data)

def deleteCategory(request):
    delete_category = dbCategory.objects.get(pk=request.GET.get('category_id'))
    delete_category_entry = dbEntry.objects.filter(category=delete_category)
    for i in delete_category_entry:
        replace_entry = dbEntry(entryUser=request.user, amount=i.amount, fromAccount=i.fromAccount, toAccount=i.toAccount, entryNote=i.entryNote, type=i.type, category=None)
        replace_entry.save()
    delete_category.delete()
    data = {
        'message': 'delete category successful',
    }
    return JsonResponse(data)

# account
def addAccount(request):
    add_account_name = request.POST['add_account_name'].lower()
    add_account_balance = request.POST.get('add_account_balance')
    if  dbAccount.objects.filter(accountUser=request.user, accountName=add_account_name).exists():
        data = {
            'message': 'Another category with the same name. Add category failed.'
        }
    elif request.method == "POST":
        add_account = dbAccount(accountUser=request.user, accountName=add_account_name, accountBalance=add_account_balance, accountType = request.POST['add_account_type'])
        add_account.save()
        account_first_entry = dbEntry(entryUser=request.user, amount=add_account_balance, fromAccount=add_account, toAccount=add_account, entryNote='new account', type='system')
        account_first_entry.save()
        data = {
            'message': 'add account successful'
        }
    return JsonResponse(data)

def editAccount(request):
    if request.method == "POST":
        edit_account = dbAccount.objects.get(pk=request.POST['account_id'])
        edit_account_balance = request.POST.get('edit_account_balance')
        edit_account_name = request.POST.get('edit_account_name').lower()
        if edit_account.accountBalance != edit_account_balance:
            balanceDiff = float(edit_account_balance) - float(edit_account.accountBalance)
            balanceDiffEntry = dbEntry(entryUser=request.user, amount=balanceDiff, fromAccount=edit_account, toAccount=edit_account, entryNote='edit balance', type='system')
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
    delete_account = dbAccount.objects.get(pk=request.POST['account_id'])
    delete_entry = dbEntry.objects.filter(fromAccount=request.POST['account_id'])| dbEntry.objects.filter(toAccount=request.POST['account_id'])
    for i in delete_entry:
        if (i.type =='transfer'):
            if (i.fromAccount==delete_account):
                replace_entry=dbEntry(entryUser=request.user, amount=i.amount, fromAccount=None, toAccount=i.toAccount, entryNote=i.entryNote, type='transfer')
            elif (i.toAccount==delete_account):
                replace_entry=dbEntry(entryUser=request.user, amount=i.amount, fromAccount=i.fromAccount, toAccount=None, entryNote=i.entryNote, type='transfer')
            replace_entry.save()
    # delete_entry.delete()
    delete_account.delete()
    # delete_entry.save()
    data = {
        'message': 'delete account successful'
    }
    return JsonResponse(data)

# signin signout
def signin(request):
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        remember_me=request.POST.get('remember-me')
        user=authenticate(request,email=email,password=password)
        if user:
            login(request,user)
            if not remember_me:
                print('not remembering you')
                request.session.set_expiry(0)
            data = {
                "message":"Login successful",
                "message_type":'success'
            }
            return HttpResponseRedirect(reverse("index"))
        else:
            data = {
                "message":"Invalid Credentials",
                "message_type":'danger'
            }
            return render(request, "walletapp/login.html", data)
    return render(request, "walletapp/login.html")

def signinfirst(request):
    data = {
        'message': 'Login first.',
        'message_type': 'danger',
        
    }
    return render(request, 'walletapp/login.html', data)

def signout(request):
    logout(request)
    data = {
        'message':'Successfully logged out.',
        'message_type':'success'
    }
    return render(request, "walletapp/login.html", data)

def register(request):
    reg_email = request.GET.get('reg_email')
    # reg_first_name = request.GET.get('reg_first_name')
    # reg_last_name = request.GET.get('reg_last_name')
    reg_password = request.GET.get('reg_password')
    reg_password2 = request.GET.get('reg_password2')
    reg_dob = request.GET.get('reg_dob')
    if not MyUser.objects.filter(email=reg_email).exists():
        if reg_password and reg_password2 and reg_password == reg_password2:
            newUser = MyUser.objects.create_user(email=reg_email,date_of_birth=reg_dob,password=reg_password)
            newUser.save()
            #new User create default category and account
            createdUser = MyUser.objects.get(email=reg_email)
            init_account = dbAccount(accountUser=createdUser, accountName='wallet', accountBalance=0, accountType = 'cash')
            init_account.save()
            account_first_entry = dbEntry(entryUser=createdUser, amount=0, fromAccount=init_account, toAccount=init_account, entryNote='new account', type='system')
            account_first_entry.save()
            init_category = dbCategory(categoryUser=createdUser, categoryName='salary', categoryType='income')
            init_category.save()
            init_category = dbCategory(categoryUser=createdUser, categoryName='others', categoryType='income')
            init_category.save()
            init_category = dbCategory(categoryUser=createdUser, categoryName='food', categoryType='expense')
            init_category.save()
            init_category = dbCategory(categoryUser=createdUser, categoryName='transport', categoryType='expense')
            init_category.save()
            init_category = dbCategory(categoryUser=createdUser, categoryName='shopping', categoryType='expense')
            init_category.save()
            init_category = dbCategory(categoryUser=createdUser, categoryName='bills', categoryType='expense')
            init_category.save()
            init_category = dbCategory(categoryUser=createdUser, categoryName='others', categoryType='expense')
            init_category.save()
            data = {
                'message': 'Registration successful. You can log in now.',
                'message_type': 'success',
                # 'reg_email':reg_email,
                # 'reg_dob':reg_dob,
                # 'reg_password':reg_password,
                # 'reg_password2':reg_password2,
                # 'reg_first_name':reg_first_name,
                # 'reg_last_name':reg_last_name,
            }
        else:
            data = {
                'message': 'Password does not match. Please try again',
                'message_type': 'danger',
            }
    else:
        data = {
                'message': 'Email address is already registered.',
                'message_type': 'danger',
        }

    return JsonResponse(data)

# export
def export(request):
    export_date_start = request.GET.get('exportDateStart')
    export_date_end = request.GET.get('exportDateEnd')
    transaction = dbEntry.objects.filter(entryUser=request.user, entryDate__range=[export_date_start, export_date_end]).defer('entryUser').exclude(type='system')
    account = dbAccount.objects.filter(accountUser=request.user)
    category = dbCategory.objects.filter(categoryUser=request.user)
    data = {
        'transaction': serializers.serialize('json', transaction),
        'account': serializers.serialize('json', account),
        'category': serializers.serialize('json', category),
    }
    return JsonResponse(data)