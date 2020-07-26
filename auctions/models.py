from django.contrib.auth.models import AbstractUser
from django.core.validators import URLValidator
from django.utils import timezone
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.CharField(max_length=64, null=True) #use a data list on form to provide options of what categories already exist. 
    imageURL = models.URLField(null=True, validators =[URLValidator])
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #create key to get user ID. 
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user')
    starting_bid = models.PositiveIntegerField()
    #create ManytoMany for watchlist 
    watchlist = models.ManyToManyField(User)


    def __str__(self):
        return f"ID: {self.id} Title:{self.title} Description:{self.description} Category:{self.category} ImageURL:{self.imageURL} Active:{self.active} Created at:{self.created_at} UserID:{self.user} WatchList:{self.watchlist})"
   
class Comments(models.Model):
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment {self.comment} listing ID:{self.listing.id} Username:{self.user})"


class Bids(models.Model):
    #starting bid ID #this should be in the listing model
    created_at = models.DateTimeField(auto_now_add=True)
    bid = models.PositiveIntegerField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Bid: {self.bid} listing ID:{self.listing.id} User_ID:{self.user})"
       

    
