import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings


def transaction_image_file_path(instance, filename):
    # generate file path for new recipe image
    extention = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{extention}'
    return os.path.join('uploads/transaction/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # Creates and saves a new user
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        # Creates and saves a new super user
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Custom user model that supports using email instead of username
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Wallet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    name = models.CharField(max_length=200)
    balance = models.IntegerField(default=0)
    currency = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    flow = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True)
    date = models.DateTimeField()
    note = models.TextField(max_length=500, blank=True, null=True)
    ammount = models.IntegerField()
    image = models.ImageField(null=True, upload_to=transaction_image_file_path)

    def __str__(self):
        return str(self.category)


class Tag(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.name)
