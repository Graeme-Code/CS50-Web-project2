from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Bids

class CreateListing(forms.Form): #note to self classes are in camelcase! 
    title = forms.CharField(label='Listing Title', max_length=64, min_length=4)
    description = forms.CharField(widget=forms.Textarea)
    category = forms.CharField(label='Category', max_length=64)
    imageURL = forms.URLField()
    starting_bid = forms.IntegerField(label="Starting Bid")

class NewBid(forms.Form):
    newbid = forms.IntegerField(label="New Bid") #This will need validation to ensure new bid is greater than old bid

def index(request):
    return render(request, "auctions/index.html", {
        "active_listings":Listing.objects.all()
    })

def listing(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        user = User.objects.get(pk = int(request.user.id))
        user_id = user.id
        newbid_value = request.POST['newbid']
        newbid = Bids(bid=newbid_value, listing_id=listing_id, user_id=user_id)
        newbid.save()
        return HttpResponseRedirect(reverse("listing",args=([listing_id]),
        ))
    else:
        #get listing
        listing = Listing.objects.get(pk=listing_id)
        #get bids
        bids = Bids.objects.filter(listing_id=listing_id).order_by("-bid")
        #get number of bids
        bids_count = bids.count()
        #get the highest bid
        highest_bid = bids.first().bid
        return render(request, "auctions/listing.html", {
            "listing":listing,
            "bid_count": bids_count,
            "highest_bid": highest_bid,
            "newbid": NewBid
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

def createlisting(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        category = request.POST['category']
        imageURL = request.POST['imageURL']
        starting_bid = request.POST['starting_bid']
        user = request.user.id #this gives me the user name. 
        user_id = User.objects.get(pk = int(user)) #trying to get rest of data of user
        print(user)
        print(user_id)
        newlisting = Listing(title=title, description=description, category=category, imageURL=imageURL, starting_bid=starting_bid)
        newlisting.user = user_id
        newlisting.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createlisting.html", {
            'form':CreateListing()
            })

    