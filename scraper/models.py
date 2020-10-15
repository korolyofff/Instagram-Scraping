from django.db import models

# Create your models here.
class Users(models.Model):
    username = models.CharField(unique=True)
    posts = models.CharField()
    subscribed_on_your_profile = models.CharField()
    following = models.CharField()
    followers = models.CharField()
    name = models.CharField