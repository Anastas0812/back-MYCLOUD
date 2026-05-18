from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):  #Django username, password, email + мои поля
    DoesNotExist = None
    full_name = models.CharField(max_length=250, blank=True)  #необязательное поле
    is_admin = models.BooleanField(default=False)
    storage_path = models.CharField(max_length=250, blank=True)
