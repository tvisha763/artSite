from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('', views.home, name='home'),
    path('post', views.post, name='post'),
    path('explore/', views.explore, name='explore'),
    path('show_art/<int:art_id>/', views.show_art, name="show_art"),
    # path('show_auction_search', views.show_auction, name="show_auction"),
    # path('show_spot', views.show_spot, name="show_spot"),
    # path('show_not_selling', views.show_not, name="show_not_selling"),
    path('artSearch', views.artSearch, name="artSearch"),
    path('artistSearch', views.artistSearch, name="artistSearch"),
    path('typeSearch', views.typeSearch, name="typeSearch"),
    path('bid', views.bid, name="bid"),
    path('like_art', views.like_art, name="like_art"),
]
