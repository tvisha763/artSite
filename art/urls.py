from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('', views.home, name='home'),
    path('post', views.post, name='post'),
    path('explore', views.explore, name='explore'),
    path('show_art', views.show_art, name="show_art"),
]
