from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
# custom user model
class MyUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password=None):
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address',max_length=255,unique=True,)
    first_name = models.CharField(verbose_name='first name',max_length=255,)
    last_name = models.CharField(verbose_name='last name',max_length=255,)
    date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'date_of_birth']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


# database models

class dbAccount(models.Model):
    accountName = models.CharField(max_length=64, null=True)
    accountBalance = models.CharField(max_length=64, null=True)
    accountType = models.CharField(max_length=64, null=True, blank=True)
    accountUser = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"[{self.accountUser}] {self.accountName} | Bal: ${self.accountBalance} ({self.accountType})"

class dbAccountType(models.Model):
    accountType = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.accountType}"

class dbCategory(models.Model):
    categoryName = models.CharField(max_length=64)
    categoryType = models.CharField(max_length=64)
    categoryUser = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"[{self.categoryUser}] {self.categoryName} ({self.categoryType})"

class dbEntry(models.Model):
    amount = models.FloatField()
    category = models.ForeignKey(dbCategory, on_delete=models.CASCADE, null=True, blank=True)
    entryTime = models.TimeField(default=now, null=True)
    entryDate = models.DateField(default=now, null=True)
    fromAccount = models.ForeignKey(dbAccount, on_delete=models.CASCADE, related_name='fromAccount', null=True, blank=True)
    toAccount = models.ForeignKey(dbAccount, on_delete=models.CASCADE, related_name='toAccount', null=True, blank=True)
    entryNote = models.CharField(max_length=64, null=True)
    entryUser = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=64)

    def __str__(self):
        return f"[{self.entryUser}] ${self.amount} ({self.category}) | from<{self.fromAccount}>to<{self.toAccount}> | {self.entryDate} | {self.entryNote} | {self.type}"
