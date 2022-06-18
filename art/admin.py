from django.contrib import admin
from django.contrib import admin
from .models import Like, User, Post, Comment



# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)