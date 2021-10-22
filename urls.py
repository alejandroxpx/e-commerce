from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name = "index"),
    path("login", views.login_view, name = "login"),
    path("logout", views.logout_view, name = "logout"),
    path("register", views.register, name = "register"),
    path("createlisting",views.createlisting, name = "createlisting"),
    path("createwatchlist/<int:listing>",views.createwatchlist, name="createwatchlist"),
    path("listing/<int:listing>",views.listing, name="listing"),
    path("comments/<int:listing>",views.comments, name = "comments"),
    path("watchlist/<int:user>",views.watchlist,name="watchlist"),
    path("deletewatchlistitem/<int:listing>",views.deletewatchlistitem, name = "deletewatchlistitem"),
    path("categories",views.categories,name="categories"),
    path("category/<str:category>",views.category,name="category"),
    path("bid/<int:listing>/<int:startingbid>",views.bid,name="bid"),
    path("closelisting/<int:listing>",views.closelisting,name="closelisting")
]
