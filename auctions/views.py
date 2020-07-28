from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Bids, Comments

class CreateListing(forms.Form): 
    title = forms.CharField(label='Listing Title', max_length=64, min_length=4, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    category = forms.CharField(label='Category', max_length=64, widget=forms.TextInput(attrs={'class': 'form-control'}))
    imageURL = forms.URLField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    starting_bid = forms.IntegerField(label="Starting Bid", widget=forms.TextInput(attrs={'class': 'form-control'}))

class NewBid(forms.Form):
    newbid = forms.IntegerField(label="New Bid",widget=forms.TextInput(attrs={'class': 'form-control'})) #This will need validation to ensure new bid is greater than old bid

class NewComment(forms.Form):
    newcomment = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

def index(request):
    return render(request, "auctions/index.html", {
        "active_listings":Listing.objects.filter(active=True)
    })

def listing(request, listing_id):
    #to refactor this so function checks if user is login in requires making each of these its own function with decortor and calling these functions indside of this method. 
    if request.method == "POST": 
        listing = Listing.objects.get(pk=listing_id)
        user = User.objects.get(pk = int(request.user.id))
        user_id = user.id
        
        #get bid info
        bids = Bids.objects.filter(listing_id=listing_id).order_by("-bid")
        #get number of bids
        bids_count = bids.count()
        #handle no bids instance. 
        if bids_count == 0:
            bid_count = "No bids"
            highest_bid = 0
        else:
            highest_bid = int(bids.first().bid)

        #handle different post requests from listing view
        if 'newbid' in request.POST:
            newbid_value = int(request.POST['newbid'])
            if newbid_value < listing.starting_bid:
                message = "bid must be greater than starting bid"
                return render(request, "auctions/error.html", {
                    "message":message
                })
    
            elif newbid_value <= highest_bid:
                message = "bid must be greater than highest bid"
                return render(request, "auctions/error.html", {
                    "message":message
                })
            else:
                newbid = Bids(bid=newbid_value, listing_id=listing_id, user_id=user_id)
                newbid.save()
        elif 'newcomment' in request.POST:
            newcomment_value = request.POST['newcomment']
            newcomment = Comments(comment=newcomment_value,listing_id=listing_id, user_id=user_id)
            newcomment.save()
        elif 'watchlist' in request.POST:
            watchlist_item = listing.watchlist.add(user)

        elif 'close' in request.POST:
            #code to close auction. 
            listing.active = False
            listing.save()
            

        return HttpResponseRedirect(reverse("listing",args=([listing_id]),
            ))
    else:
        #get listing
        listing = Listing.objects.get(pk=listing_id)
        #get bids
        bids = Bids.objects.filter(listing_id=listing_id).order_by("-bid")
        #get number of bids
        bids_count = bids.count()
        #create default for hightest bid user
        highest_bid_user = "No one"
        #handle no bids instance. 
        if bids_count == 0:
            bid_count = "No bids"
            highest_bid = 0
        else:
            highest_bid = bids.first().bid
            highest_bid_user = bids.first().user
        #get comments
        try:
            comments = Comments.objects.filter(listing_id=listing_id)
        except:
            comments = "No comments" #reminder, use if statement view to dynamically render this. 

        #Check if vistor is auther
        is_author = False
        try:
            user = User.objects.get(pk = int(request.user.id))
            author = listing.user
            if author == user:
                is_author = True
        except:
            is_author = False

        #Check if user is creator of highest bid when listing is closed
        is_winner = False
        if listing.active == False and user == highest_bid_user:
            is_winner = True
            
        return render(request, "auctions/listing.html", {
            "listing":listing,
            "bid_count": bids_count,
            "highest_bid": highest_bid,
            "newbid": NewBid,
            "comments": comments,
            "newcomment":NewComment,
            "is_author":is_author,
            "is_winner":is_winner
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

@login_required(login_url='/login/') 
def createlisting(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        category = request.POST['category']
        imageURL = request.POST['imageURL']
        starting_bid = request.POST['starting_bid']
        user = request.user.id #this gives me the user name. 
        user_id = User.objects.get(pk = int(user)) #trying to get rest of data of user
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
    cateogry = category
    category_listing = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        'category_listing': category_listing,
        'category': category
    })

@login_required(login_url='/login/') 
def watchlist(request):
    
    #get user Id
    user = User.objects.get(pk = int(request.user.id))
    #get items on users waatchlist
    watchedlistings = Listing.objects.filter(watchlist = user)
   

    return render(request, "auctions/watchlist.html",{
        'watchedlistings':watchedlistings

    })
    