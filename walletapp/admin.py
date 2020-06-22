from django.contrib import admin
from .models import dbEntry, dbAccount, dbAccountType, dbCategory

# Register your models here.

admin.site.register(dbEntry)
admin.site.register(dbAccount)
admin.site.register(dbAccountType)
admin.site.register(dbCategory)
