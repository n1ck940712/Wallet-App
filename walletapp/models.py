from django.db import models
from django.utils.timezone import now

# Create your models here.



class dbAccount(models.Model):
    accountName = models.CharField(max_length=64, null=True)
    accountBalance = models.CharField(max_length=64, null=True)
    accountType = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"{self.accountName} ({self.accountType}) - Balance: {self.accountBalance}"

class dbAccountType(models.Model):
    accountType = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.accountType}"

class dbCategory(models.Model):
    categoryName = models.CharField(max_length=64)
    categoryType = models.CharField(max_length=64)

    def __str__(self):
        return f"({self.categoryType}) {self.categoryName}"

class dbEntry(models.Model):
    amount = models.FloatField()
    category = models.ForeignKey(dbCategory, on_delete=models.CASCADE, null=True)
    entryTime = models.TimeField(default=now, null=True)
    entryDate = models.DateField(default=now, null=True)
    fromAccount = models.ForeignKey(dbAccount, on_delete=models.CASCADE, related_name='fromAccount', null=True, blank=True)
    toAccount = models.ForeignKey(dbAccount, on_delete=models.CASCADE, related_name='toAccount', null=True, blank=True)
    entryNote = models.CharField(max_length=64, null=True)
    type = models.CharField(max_length=64)

    def __str__(self):
        return f"${self.amount} ({self.category}) | from<{self.fromAccount}>to<{self.toAccount}> | {self.entryTime}-{self.entryDate} | {self.entryNote} | {self.type}"
