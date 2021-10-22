from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.enums import Choices


class User(AbstractUser):
    def __str__(self):
        return f"{self.id} {self.username} {self.password}"

class AuctionListing(models.Model): # This model will create this table and insert this data into the table
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    startingbid = models.IntegerField()
    url = models.URLField(max_length=500,blank=True)
    CATEGORY_CHOICES = (
        ('FASH','Fashion'),
        ('TOYs','Toys'),
        ('ELEC','Electronics'),
        ('HOME','Home'),
        ('None', 'None')
    )
    category = models.CharField(max_length=4, choices = CATEGORY_CHOICES, default = 'None')
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user")
    active = models.IntegerField(default=True)
    winner = models.ForeignKey(User,on_delete=models.CASCADE,null=True, default = None)
    def __str__(self):
        return f" {self.id}: {self.title}: {self.description}:  {self.startingbid}: {self.url}: {self.category}"

class Bids(models.Model):
    bid = models.IntegerField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=None)
    listing = models.ForeignKey(AuctionListing,on_delete=models.CASCADE,default=None)
    winner = models.ForeignKey(User,on_delete=models.CASCADE, null = True, default = None, related_name="bidwinner")
    class Meta:
        unique_together = ["user","bid","listing"]
    def __str__(self):
        return f"Bid: {self.bid} {self.user} {self.listing}"

class Comments(models.Model):
    comment = models.CharField(max_length=255)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,default=None)
    listing_id = models.ForeignKey(AuctionListing,on_delete=models.CASCADE,default=None)
    def __str__(self):
        return f"Comments: {self.comment} : {self.user_id} : {self.listing_id}"

class Watchlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="watchlistuser")
    listing = models.ForeignKey(AuctionListing, default=None,on_delete=models.CASCADE)
    class Meta:
        unique_together = ["user","listing"]
    def __str__(self):
        return f"Watchlist: {self.id} {self.user} {self.listing}"

