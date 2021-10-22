from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.query import EmptyQuerySet
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import User, AuctionListing, Watchlist, Bids, Comments

def index(request):
    return render(request, "auctions/index.html",{
        "auctionlist": AuctionListing.objects.all(),
        "bid":Bids.objects.all(),
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

class NewAuctionListing(forms.Form):
    title = forms.CharField(label="Title ")
    description = forms.CharField(label="Description ")
    startingbid = forms.FloatField(label="Starting bid ")
    url = forms.CharField(label="URL ", required=False)
    CATEGORY_CHOICES = (
        ('FASH','Fashion'),
        ('TOYs','Toys'),
        ('ELEC','Electronics'),
        ('HOME','Home'),
        ('None', 'None')
    )
    category = forms.ChoiceField(label="Category ",choices=CATEGORY_CHOICES, required=False)

def createlisting(request):
    if request.method == "POST":
        form = NewAuctionListing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            startingbid = form.cleaned_data["startingbid"]
            url = form.cleaned_data["url"]
            category = form.cleaned_data["category"]
            AuctionListing.objects.create(
                title=title.capitalize(),
                description=description,
                startingbid=startingbid,
                url=url,
                category=category,
                user = request.user
                )
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/createlisting.html",{
                "form":form
            })
    return render(request,"auctions/createlisting.html",{
        "form" : NewAuctionListing()
    })

def watchlist(request, user):
    watchlist = Watchlist.objects.filter(user=user).all()
    return render(request,"auctions/watchlist.html",{
        "watchlist": watchlist
    })
@login_required
def createwatchlist(request,listing):
    if request.method == "GET":
        user = request.user
        listing = AuctionListing.objects.get(pk=listing)  
        # Check if listing is already in watchlist
        if Watchlist.objects.filter(user=user,listing=listing):
            return render(request,"auctions/listing.html",{
                "listing":listing,
                "message":"Item already in watchlist"
            })
        # Item wasn't found in db   
        else: 
            watchlist = Watchlist(user=user,listing=listing)
            watchlist.save()
            watchlist = Watchlist.objects.filter(user=user).all()
            return render(request,"auctions/watchlist.html",{
                "watchlist":watchlist
            })
    else:
        return HttpResponse('Error within the listing or user,')

class PlaceBid(forms.Form):
    bid = forms.FloatField(label="bid")

def bid(request,listing,startingbid):
    if request.method == "POST":

        # Get the bid from the user
        form = PlaceBid(request.POST)

        if form.is_valid():

            bid = form.cleaned_data["bid"]
            print(f"{bid}")
            user = request.user
            listing = AuctionListing.objects.get(pk = listing)
            # If a bid already exsist go into loop
            if Bids.objects.filter(listing = listing, user=user).all():
                # Check if bid is greater than starting bid
                if (bid >= startingbid):
                    maxbid = Bids.objects.filter(listing = listing).order_by("-bid").first()
                    print(f"max bid: {maxbid.bid}") # {'bid__max' : 200} 
                 
                    if (bid > maxbid.bid): # hard coded value for now
                        return render(request, "auctions/listing.html",{
                            "listing":listing,
                            "bid":bid,
                        })
                    else:
                        return render(request, "auctions/listing.html",{
                            "listing":listing,
                            "message":"Bid must be greater than highest bid.",
                            "highest_bid":maxbid
                        })
                else: 
                    return render(request, "auctions/listing.html",{
                        "listing":listing,
                        "message":"Bid must be greater than starting bid."
                    })
            # If there are no biding yet go into loop
            else:
                if (bid >= startingbid):
                    if Bids.objects.filter(listing = listing).order_by("-bid").first():
                        maxbid = Bids.objects.filter(listing = listing).order_by("-bid").first()
                        if (bid > maxbid.bid): # in this case the maximum bid is the starting bid
                            createbid = Bids(listing=listing,user=user,bid=bid) # Add bid to db
                            createbid.save()
                            return render(request, "auctions/listing.html",{
                                "listing":listing,
                                "bid":bid,
                            })
                        else:
                            return render(request, "auctions/listing.html",{
                                "listing":listing,
                                "message":"Bid must be greater than highest bid.",
                                "highest_bid":maxbid
                            })
                    else: 
                        createbid = Bids(listing=listing,user=user,bid=bid) # Add bid to db
                        createbid.save()
                        return render(request, "auctions/listing.html",{
                            "listing":listing,
                            "bid":bid,
                            "message":"Bid saved"
                        })
                else: 
                    return render(request, "auctions/listing.html",{
                        "listing":listing,
                        "message":"Bid must be greater than starting bid."
                    })
        else: 
            return HttpResponse("Check point 3")
    return render(request, "auctions/listing.html",{
        "form":PlaceBid()
        })

def listing(request,listing): 
    listing = AuctionListing.objects.get(id = listing)
    comment = Comments.objects.filter(listing_id = listing).all()
    print(f"{comment}")
    maxbid = Bids.objects.filter(listing = listing).order_by("-bid").first()
    return render(request, "auctions/listing.html",{
        "listing":listing,
        "comment":comment,
        "maxbid":maxbid
    })

class MakeComment(forms.Form):
    comment = forms.CharField(label="comment")

def comments(request, listing ):
    if request.method == "POST":
        form = MakeComment(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            print(f"{comment}")
            user = request.user
            listing = AuctionListing.objects.get(pk = listing)
            addcomment = Comments(comment = comment,user_id=user,listing_id=listing)
            addcomment.save()
            comments = Comments.objects.filter(listing_id = listing).all()
            print(f"{comments}")
            return render(request, "auctions/listing.html",{
                "listing": listing,
                "comment":comments
            })
        else:
            return HttpResponse("error")
    else:
        return HttpResponse("Failed before form")
   
def deletewatchlistitem(request,listing):
    user = request.user
    listing = Watchlist.objects.get(user=user,listing=listing)
    listing.delete()
    watchlist = Watchlist.objects.filter(user=user).all()
    return render(request,"auctions/watchlist.html",{
        "watchlist": watchlist
    })

def category(request,category):
    listing = AuctionListing.objects.filter(category=category).all()
    print(f"{listing}")
    return render(request,"auctions/category.html",{
        "listing":listing,
        "category":category
    })

def categories(request):
    Home = AuctionListing.objects.filter(category = 'HOME').all()
    Electronic = AuctionListing.objects.filter(category = 'ELEC').all()
    Toy = AuctionListing.objects.filter(category = 'TOYs').all()
    Fashion = AuctionListing.objects.filter(category = 'FASH').all()
    none =  AuctionListing.objects.filter(category = 'None').all()
    return render(request,"auctions/categories.html",{
        "Home":Home,
        "Electronic":Electronic,
        "Fashion":Fashion,
        "Toy":Toy,
        "none":none
    })

def closelisting(request,listing):
    listing_id = listing
    user = request.user
    item = AuctionListing.objects.filter(id = listing_id, user = user).update(active = False)
    print(item)
    maxbid = Bids.objects.filter(listing = listing).order_by("-bid").first()
    winner = Bids.objects.filter(listing = listing).order_by("-bid").first()
    winner.save()
    item = AuctionListing.objects.filter(id = listing_id, user = user).update(winner = winner.user.id)

    return render(request,"auctions/index.html",{
        "auctionlist": AuctionListing.objects.all(),
        "bid":winner,
        "maxbid":maxbid
    })