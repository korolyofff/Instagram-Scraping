from django.db import models


class Users(models.Model):
    username = models.CharField(max_length=100)
    posts = models.CharField(max_length=100)
    subscribed_on_your_profile = models.CharField(max_length=50)
    you_subscribed = models.CharField(max_length=50)
    following = models.CharField(max_length=100)
    followers = models.CharField(max_length=100)
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250, )
    picture = models.URLField(max_length=255)
    email = models.EmailField(max_length=100)


class LoginData(models.Model):
    login = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
