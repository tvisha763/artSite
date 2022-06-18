from django.db import models
from django.forms import CharField
from django.utils import timezone

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, default='')
    password = models.CharField(max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    salt = models.CharField(max_length=1023)
    def __str__(self):
        return '%s - %s' % (self.username, self.email)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    
