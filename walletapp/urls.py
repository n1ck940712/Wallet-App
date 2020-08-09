from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('overview', views.overview, name='overview'),
    path('settingPage', views.settingPage, name='settingPage'),
    # signin signout
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    # account graph data
    path('getAccountOverview', views.getAccountOverview, name='getAccountOverview'),
    # entry
    path('addEntry', views.addEntry, name='addEntry'),
    path('editEntry', views.editEntry, name='editEntry'),
    path('editEntryConfirm', views.editEntryConfirm, name='editEntryConfirm'),
    path('deleteEntry', views.deleteEntry, name='deleteEntry'),
    path('loadEntry', views.loadEntry, name='loadEntry'),
    # category
    path('addCategory', views.addCategory, name='addCategory'),
    path('editCategory', views.editCategory, name='editCategory'),
    path('deleteCategory', views.deleteCategory, name='deleteCategory'),
    path('loadCategory', views.loadCategory, name='loadCategory'),
    # account
    path('addAccount', views.addAccount, name='addAccount'),
    path('editAccount', views.editAccount, name='editAccount'),
    path('deleteAccount', views.deleteAccount, name='deleteAccount'),
    path('loadAccount', views.loadAccount, name='loadAccount')

]
