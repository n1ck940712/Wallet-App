from django.db import models
from django.utils.timezone import now

# Create your models here.

class entry(models.Model):
    amount = models.FloatField()
    category = models.CharField(max_length=64)
    entry_time = models.TimeField(default=now, blank=True)
    entry_date = models.DateField(default=now, blank=True)

    def __str__(self):
        return f"{self.amount} | {self.category} | {self.entry_time} | {self.entry_date}"
