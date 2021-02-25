from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Watchlist, Bid, Comment
import datetime

from .modelforms import CommentForm, BidForm

def index(request):
    return render(request, "auctions/index.html", {
        "message": False,
        "listings": Listing.objects.filter(is_active=True)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def add(request):
    if request.method == "POST":
        category_id = int(request.POST["category"])
        category = Category.objects.get(pk=category_id)
        title = request.POST["title"]
        description = request.POST["description"]
        start_price = int(request.POST["start_price"])
        image_url = request.POST["image_url"]
        user = get_user(request)
        date = datetime.datetime.now()
        
        new_listing = Listing.objects.create(
            user=user,
            category=category,
            title=title,
            description=description,
            date=date,
            start_price=start_price,
            current_price=start_price,
            image_url=image_url)
        new_listing.save()
        # REDIRIGER VERS LA PAGE DU LISTING (quand elle sera créé)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/add.html", {
            "categories": Category.objects.all()
        })

def listing(request, listing_id):
    user=get_user(request)
    error_msg=""
    message_winner=""

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        watched_listings = user.watcher.values_list("listing", flat=True)
        
        # simulate a switch, based on "action" to deal with toggling the watchlist, comment, bid.
        action = request.POST["action"]
        if action == "toggle_watchlist":
            if listing.id in watched_listings:
                wl_obj = user.watcher.filter(listing=listing.id)
                wl_obj.delete()
            else:
                wl_obj = Watchlist(user=user, listing=listing)
                wl_obj.save()
        if action == "place_bid":
            bid_form = BidForm(request.POST)
            bid_form.is_valid()
            bid_price = bid_form.cleaned_data["price"]
            # get bids on this listing
            bids = listing.bided.all()
            bids_count = bids.count()
            # if no bid --> check if bid_price > starting price
            if bids_count == 0:
                if bid_price >= listing.start_price:
                    bid_entry = Bid(listing=listing, user=user, price=bid_price)
                    bid_entry.save()
                    listing.current_price = bid_price
                    listing.save()
                else:
                    error_msg="Your bid must be equal or higher than the starting price."
            # else (there are bid(s)) --> check id bid_price > current price (= highest bid)
            else:
                bids_highest = bids.order_by("price").last().price
                if bid_price > bids_highest:
                    bid_entry = Bid(listing=listing, user=user, price=bid_price)
                    bid_entry.save()
                    listing.current_price = bid_price
                    listing.save()
                else:
                    error_msg="Your bid must be equal or higher than the current price"
        if action == "close_auction":
            listing.is_active = False
            listing.save()
            # the user with the highest bid has a message on the listing page (which is inactive: user has to access the listing by typing his url)
        if action == "add_comment":
            comment_form = CommentForm(request.POST)
            comment_form.is_valid()
            comment = comment_form.cleaned_data['text']
            comment_obj = Comment(listing=listing, user=user, text=comment)
            comment_obj.save()
        # end of switch
        if listing.id in user.watcher.values_list("listing", flat=True):
            is_watched = True
        else:
            is_watched = False
    # GET method
    else:
        # check if the asked listing exist (active or not)
        listings_id = Listing.objects.values_list("id", flat=True)
        message_winner=""
        
        if listing_id in listings_id:
            listing = Listing.objects.get(pk=listing_id)
            # check if this listing is in the user watchlist (add manage the watchlist button)
            is_watched = False
            # if user is logged in, get his watchlist and update is_watched
            if user.is_authenticated:
                watcheds = Watchlist.objects.filter(user=user).values_list("listing", flat=True)
                if listing_id in watcheds:
                    is_watched = True
                if not listing.is_active and listing.bided.order_by("price").last().user == user:
                    message_winner = "You won this auction"
        # if the asked listing doesn't exist, redirect to index + a fail message
        else:
            return render(request, "auctions/index.html", {
                "message": True,
                "listings": Listing.objects.filter(is_active=True)
            })
    # Generate the views for both GET and POST method
    return render(request, "auctions/listing.html", {
                "listing": listing,
                "is_watched": is_watched,
                "bids_count": listing.bided.all().count(), 
                "bid_form": BidForm(),
                "error_msg": error_msg,
                "message_winner": message_winner,
                "comment_form": CommentForm(),
                "comments": listing.commented.all().order_by("date").reverse()
            })

@login_required
def watchlist(request):
    user = get_user(request)
    watchlist = user.watcher.all()
    listings_id = watchlist.values_list("listing", flat=True)
    listings = Listing.objects.filter(id__in=listings_id)
    print(listings)
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

def category(request, category_id):
    cat_id_list = Category.objects.all().values_list("id", flat=True)
    if category_id in cat_id_list:
        category = Category.objects.get(id=category_id)
        listings = Listing.objects.filter(category=category, is_active=True)
        return render(request, "auctions/category.html", {
            "category": category,
            "listings": listings
        })
    else: 
        return HttpResponseRedirect(reverse("categories"))