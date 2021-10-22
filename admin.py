from auctions.views import createlisting, listing
from django.contrib import admin
from .models import User, AuctionListing, Bids, Comments, Watchlist

class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username","email","password")

class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ("id","title","description","startingbid","url","category","active")

class BidsAdmin(admin.ModelAdmin):
    list_display = ("id","bid")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id","user")

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id","comment")

# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(AuctionListing,AuctionListingAdmin)
admin.site.register(Bids,BidsAdmin)
admin.site.register(Watchlist,WatchlistAdmin)
admin.site.register(Comments,CommentsAdmin)