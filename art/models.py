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
    SALE_CHOICES = [
        (1, 'Auction'),
        (2, 'Spot Sale'),
        (3, 'Not for Sale')
    ]

    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="media")
    description = models.CharField(max_length=500, blank=True)
    sale_type = models.IntegerField(default=3, choices=SALE_CHOICES)
    date_posted = models.DateTimeField(auto_now_add=True)
    # If sale type is auction, the price field will have the value of the floor price.
    price = models.IntegerField(blank=True, null=True)
    auction = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.title} - {self.artist.username}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_comments")
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user

# How the auction field looks like
'''aution = {
    'latest_bid': 50,
    'end_date': 'yyyy-mm-dd',
    'offers': [
        {
            'user_id': 2,
            'bid': 45
        },
        {
            'user_id': 3,
            'bid': 50 # The highest bid
        }
    ]
}'''
