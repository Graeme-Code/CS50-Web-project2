from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Bids, Comments

class CreateListing(forms.Form): #note to self classes are in camelcase! 
    title = forms.CharField(label='Listing Title', max_length=64, min_length=4)
    description = forms.CharField(widget=forms.Textarea)
    category = forms.CharField(label='Category', max_length=64)
    imageURL = forms.URLField()
    starting_bid = forms.IntegerField(label="Starting Bid")

class NewBid(forms.Form):
    newbid = forms.IntegerField(label="New Bid") #This will need validation to ensure new bid is greater than old bid

class NewComment(forms.Form):
    newcomment = forms.CharField(widget=forms.Textarea)

def index(request):
    return render(request, "auctions/index.html", {
        "active_listings":Listing.objects.all()
    })

def listing(request, listing_id):
    if request.method == "POST": 
        print(request)
        listing = Listing.objects.get(pk=listing_id)
        user = User.objects.get(pk = int(request.user.id))
        user_id = user.id
        #handle different post requests from listing view
        if 'newbid' in request.POST:
            newbid_value = request.POST['newbid']
            newbid = Bids(bid=newbid_value, listing_id=listing_id, user_id=user_id)
            newbid.save()
        elif 'newcomment' in request.POST:
            newcomment_value = request.POST['newcomment']
            print(newcomment_value)
            newcomment = Comments(comment=newcomment_value,listing_id=listing_id, user_id=user_id)
            newcomment.save()
        elif 'watchlist' in request.POST:
            print(user_id)
            print(user)
            watchlist_item = listing.watchlist.add(user)
            print(watchlist_item)

        return HttpResponseRedirect(reverse("listing",args=([listing_id]),
            ))
    else:
        #get listing
        listing = Listing.objects.get(pk=listing_id)
        #get bids
        bids = Bids.objects.filter(listing_id=listing_id).order_by("-bid")
        #get number of bids
        bids_count = bids.count()
        #handle no bids instance. 
        if bids_count == 0:
            bid_count = "No bids"
            highest_bid ="No bids"
        else:
            highest_bid = bids.first().bid

        #get comments
        try:
            comments = Comments.objects.filter(listing_id=listing_id)
        except:
            comments = "No comments" #reminder, use if statement view to dynamically render this. 

        return render(request, "auctions/listing.html", {
            "listing":listing,
            "bid_count": bids_count,
            "highest_bid": highest_bid,
            "newbid": NewBid,
            "comments": comments,
            "newcomment":NewComment
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

def categories(request):
    #all_listings = list(Listing.objects.values('category').distinct())
    return render(request, "auctions/categories.html", {
        'categories': list(Listing.objects.values('category').distinct())
    })

def category(request, category):
    print(category)
    cateogry = category
    category_listing = Listing.objects.filter(category=category)
    print(category_listing)
    return render(request, "auctions/category.html", {
        'category_listing': category_listing,
        'category': category
    })

def watchlist(request):
    
    #get user Id
    user = User.objects.get(pk = int(request.user.id))
    #get items on users waatchlist
    watchedlistings = Listing.objects.filter(watchlist = user)
   

    return render(request, "auctions/watchlist.html",{
        'watchedlistings':watchedlistings

    })
    