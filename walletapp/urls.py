from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('addEntry', views.addEntry, name='addEntry'),
    path('deleteEntry', views.deleteEntry, name='deleteEntry')

]
