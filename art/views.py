from contextvars import Context
from operator import contains
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Post
import bcrypt
import requests
import urllib
import os

# Create your views here.
def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        password = request.POST.get('password').encode("utf8")
        confirmPass = request.POST.get('confirmPass').encode("utf8")
        inputs = [email, username, password, confirmPass, phone]

        # checking if confirm password matches password   
        if (password != confirmPass):
            messages.error(request, "The passwords do not match.")
            return redirect('signup')

        for inp in inputs:
            if inp == '':
                messages.error(request, "Please fill all the boxes.")
                return redirect('signup')

        if password != '' and len(password) < 6:
            messages.error(request, "Your password must be at least 6 charecters.")
            return redirect('signup')
        

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. If this is you, please log in.")
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "An account with this username already exists. Please pick another one.")
            return redirect('signup')

        else:
            salt = bcrypt.gensalt()
            user = User()
            user.email = email
            user.username = username
            user.phone = phone
            user.password = bcrypt.hashpw(password, salt)
            user.salt = salt
            user.save()
            return redirect('login')
    else:
        if request.session.get('logged_in'):
            return redirect('/')

    return render(request, 'auth/signup.html')

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password').encode("utf8")
        inputs = [email, password]

        for inp in inputs:
            if inp == '':
                messages.error(request, "Please fill all the boxes.")
                return redirect('login')

        if "@" not in email:
            messages.error(request, "Please enter your email address.")
            return redirect('login')

        if User.objects.filter(email=email).exists():
            saved_hashed_pass = User.objects.filter(email=email).get().password.encode("utf8")[2:-1]
            saved_salt = User.objects.filter(email=email).get().salt.encode("utf8")[2:-1]
            user  = User.objects.filter(email=email).get()
            request.session["username"] = user.username
            request.session['logged_in'] = True
           
            salted_password = bcrypt.hashpw(password, saved_salt)
            if salted_password == saved_hashed_pass:
                return redirect('dashboard')
            else:
                messages.error(request, "Your password is incorrect.")
                return redirect('login')

        else:
            messages.error(request, "An account with this email does not exist. Please sign up.")
            return redirect('login')

    else:
        if request.session.get('logged_in'):
            return redirect('/')

    return render(request, 'auth/login.html')

def logout(request):
    if not request.session.get('logged_in') or not request.session.get('username'):
        return redirect('/login')
    else:
        request.session["username"] = None
        request.session['logged_in'] = False
        return redirect('/login')

def home(request):
    if request.session.get('logged_in'):
        return redirect('dashboard')
    return render(request, 'home.html')

def post(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "POST":       
        user = User.objects.get(username=request.session["username"])
        
        # Fetching form data
        image = request.FILES.get('image')
        title = request.POST.get('title')
        sale_type = request.POST.get('sale-type')
        description = request.POST.get('description')
        listing_price = request.POST.get('listing_price')
        floor_price = request.POST.get('floor_price')
        end_date = request.POST.get('end_date')

        if Post.objects.filter(title=title).exists():
            messages.error(request, "A post with the same title exists. Please try another title.")
            return redirect('post')
        if sale_type == "1":
            inputs = [image, title, sale_type, description, floor_price, end_date]
            for inp in inputs:
                if inp == '' or inp == None:
                    messages.error(request, "Please fill all the boxes.")
                    return redirect('post')
            auction = {'latest_bid': None, 'end_date': end_date, 'offers': []}
            post = Post(image=image, title=title, sale_type=int(sale_type), description=description, 
                artist=user, price=int(floor_price), auction=auction)
            post.save()
        elif sale_type == "2":
            inputs = [image, title, sale_type, description, listing_price]
            for inp in inputs:
                if inp == '' or inp == None:
                    messages.error(request, "Please fill all the boxes.")
                    return redirect('post')
            post = Post(image=image, title=title, sale_type=int(sale_type), description=description, 
                artist=user, price=int(listing_price))
            post.save()
        elif sale_type == "3":
            inputs = [image, title, sale_type, description]
            for inp in inputs:
                if inp == '' or inp == None:
                    messages.error(request, "Please fill all the boxes.")
                    return redirect('post')
            post = Post(image=image, title=title, sale_type=int(sale_type), description=description, 
                artist=user)
            post.save()
        else:
            messages.error(request, "Choose a type of sale.")
            return redirect('post')
        return redirect('explore')
    else:
        return render(request, 'postArtwork.html')


def dashboard(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    return render(request, 'dashboard.html')

def show_art(request, art_id):
    art = Post.objects.get(id=art_id)
    context = {'art': art}
    return render(request, 'show_art.html', context)

# def show_auction(request):
#     buttonClicked = request.POST.get("artToView")
#     info = Post.objects.get(title=buttonClicked)
#     print (buttonClicked)

#     if info.auction.get("latest_bid") == None:
#         info.auction["latest_bid"] = info.price
#         info.save

#     title = info.title
#     print(info.title)
#     context={
#         'title':info.title,
#         'artist':info.artist.username,
#         'image':info.image,
#         'description':info.description,
#         'floor':info.price,
#         'latest':info.auction.get("latest_bid"),
#         'offers':info.auction.get("offers"),
#     }
#     global currentPage
#     currentPage = info.title
#     return render(request, 'artAuction.html', context)

# def show_spot(request):
#     buttonClicked = request.POST.get("artToView")
#     info = Post.objects.get(title=buttonClicked)
    
#     context={
#         'title':info.title,
#         'phone':info.artist.phone,
#         'email':info.artist.email,
#         'artist':info.artist.username,
#         'image':info.image,
#         'description':info.description,
#         'price':info.price,
#     }
#     return render(request, 'artSpot.html', context)

# def show_not(request):
#     buttonClicked = request.POST.get("artToView")
#     info = Post.objects.get(title=buttonClicked)
    
#     context={
#         'title':info.title,
#         'phone':info.artist.phone,
#         'email':info.artist.email,
#         'artist':info.artist.username,
#         'image':info.image,
#         'description':info.description,
#     }
#     return render(request, 'artNot.html', context)

def explore(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        info = Post.objects.all()
        context = {'details': info}
        return render(request, 'explore.html', context)

def artSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("artSearch")
        info = Post.objects.filter(title__contains=Searched)    
        context={'details' : info}
        return render(request, 'explore.html', context)


def artistSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("artistSearch")
        info = Post.objects.filter(artist__username__contains=Searched)        
        context={'details' : info}
        return render(request, 'explore.html', context)


def typeSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("typeSearch")
        if int(Searched) == 0:
            info = Post.objects.all()
        else:
            info = Post.objects.filter(sale_type=int(Searched))

        context = {'details': info}
        return render(request, 'explore.html', context)

def bid(request):
    buttonClicked = request.POST.get("artToView")
    print (buttonClicked)
    # info = Post.objects.get(title=buttonClicked)
    # info.auction.get("latest_bid")
    # print(currentPage)
    # print(info.auction.get("latest_bid"))
    # context={
    #     'title':info.title,
    #     'phone':info.artist.phone,
    #     'email':info.artist.email,
    #     'artist':info.artist.username,
    #     'image':info.image,
    #     'description':info.description,
    #     'price':info.price,
    # }
    return render(request, 'artAuction.html')