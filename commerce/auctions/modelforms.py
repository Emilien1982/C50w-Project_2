from django.forms import ModelForm, Textarea, NumberInput
from django.utils.translation import gettext_lazy as _
from .models import User, Category, Listing, Watchlist, Bid, Comment

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={'style': "width: 100%; min-width: 300px", 'rows': 5, 'placeholder': "Type your comment"}),
        }
        labels = {
            'text': "",
        }

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price']
        widgets = {
            'price': NumberInput(attrs={'placeholder': "Bid (US$)", 'style': "display: block;"}),
        }
        labels = {
            'price': "",
        }