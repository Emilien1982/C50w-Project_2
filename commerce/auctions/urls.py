from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category/<int:category_id>", views.category, name="category"),
    path("categories", views.categories, name="categories"),
    path("add", views.add, name="add"),
    path("user_page/<int:user_id>", views.user_page, name="user_page"),
    path("listing/<int:listing_id>", views.listing, name="listing")
]
