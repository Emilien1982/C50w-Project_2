from django.forms import ModelForm
from .models import User, Category, Listing, Watchlist, Bid, Comment

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
