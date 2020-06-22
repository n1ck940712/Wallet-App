from django.db import models
from django.utils.timezone import now

# Create your models here.

class dbEntry(models.Model):
    amount = models.FloatField()
    category = models.CharField(max_length=64)
    entryTime = models.TimeField(default=now)
    entryDate = models.DateField(default=now)
    fromAccount = models.CharField(max_length=64)
    toAccount = models.CharField(max_length=64)

    def __str__(self):
        return f"${self.amount} ({self.category}) | from<{self.fromAccount}>to<{self.toAccount}> | {self.entryTime}-{self.entryDate}"

class dbAccount(models.Model):
    accountName = models.CharField(max_length=64)
    accountBalance = models.CharField(max_length=64)
    accountType = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.accountName} ({self.accountType}) - Balance: {self.accountBalance}"

class dbAccountType(models.Model):
    accountType = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.accountType}"

class dbCategory(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"
