from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=30)

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="category")
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    start_price = models.IntegerField(validators=[MinValueValidator(0)])
    current_price = models.IntegerField(validators=[MinValueValidator(0)])
    image_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bided")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bider")
    date = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField()

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.DO_NOTHING, related_name="commented")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="commenter")
    date = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=500)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watched")

    def __str__(self):
        return f"user {self.user} watches listing {self.listing}"
