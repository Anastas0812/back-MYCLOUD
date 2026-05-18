from django.db import models
from users.models import User


class File(models.Model):
    objects = None
    DoesNotExist = None
    # каскад=если удалена запись о юзере, то и запись о файле будет удалена
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=250)
    size = models.BigIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    last_download = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    file_path = models.CharField(max_length=500)
    special_link = models.CharField(max_length=100, unique=True, blank=True)
