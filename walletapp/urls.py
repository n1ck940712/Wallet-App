from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('loadEntry', views.loadEntry, name='loadEntry'),
    path('overview', views.overview, name='overview'),
    path('overviewAjax', views.overviewAjax, name='overviewAjax'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('addEntry', views.addEntry, name='addEntry'),
    path('deleteEntry', views.deleteEntry, name='deleteEntry'),
    path('editEntry', views.editEntry, name='editEntry'),
    path('editEntryConfirm', views.editEntryConfirm, name='editEntryConfirm'),
    path('settingPage', views.settingPage, name='settingPage'),
    path('deleteCategory', views.deleteCategory, name='deleteCategory'),
    path('editCategory', views.editCategory, name='editCategory'),
    path('addCategory', views.addCategory, name='addCategory'),
    path('deleteAccount', views.deleteAccount, name='deleteAccount'),
    path('loadCategory', views.loadCategory, name='loadCategory'),
    path('editAccount', views.editAccount, name='editAccount'),
    path('addAccount', views.addAccount, name='addAccount'),
    path('loadAccount', views.loadAccount, name='loadAccount')

]
