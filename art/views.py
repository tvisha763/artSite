from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Post, Like, Comment
import bcrypt
import requests
import urllib
import os
from datetime import datetime

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

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
    if request.method == "GET":
        user=request.session.get('username')
        info = Post.objects.filter(artist__username=user)        
        context={'details' : info}
 

    return render(request, 'dashboard.html', context)

def show_art(request, art_id):
    user = User.objects.get(username=request.session["username"])

    art = Post.objects.get(id=art_id)
    no_of_likes = Like.objects.filter(post=art).count()
    liked = Like.objects.filter(post=art, user=user).exists()
    comments = Comment.objects.filter(post=art)

    context = {'no_of_likes': no_of_likes, 'liked': liked, 'art': art, 'comments': comments}
    if art.auction != None:
        user_bid = 0
        for i in art.auction['offers']:
            if i['user_id'] == user.id:
                if i['bid'] > user_bid:
                    user_bid = i['bid']
        context['user_bid'] = user_bid

    return render(request, 'show_art.html', context)


def explore(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        user = User.objects.get(username=request.session["username"])
        info = Post.objects.exclude(artist=user)
        context = {'details': info}
        return render(request, 'explore.html', context)

def artSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("artSearch")
        user = User.objects.get(username=request.session["username"])
        info = Post.objects.filter(title__contains=Searched)    
        context={'details' : info.exclude(artist=user)}
        return render(request, 'explore.html', context)


def artistSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("artistSearch")
        user = User.objects.get(username=request.session["username"])
        info = Post.objects.filter(artist__username__contains=Searched)        
        context={'details' : info.exclude(artist=user)}
        return render(request, 'explore.html', context)


def typeSearch(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method == "GET":
        Searched = request.GET.get("typeSearch")
        user = User.objects.get(username=request.session["username"])
        if int(Searched) == 0:
            info = Post.objects.all()
        else:
            info = Post.objects.filter(sale_type=int(Searched))

        context = {'details': info.exclude(artist=user)}
        return render(request, 'explore.html', context)

def bid(request):
    if request.method == "POST":
        art = Post.objects.get(id=request.POST.get('art'))
        bid = int(request.POST.get('bid'))
        latest_bid = art.auction['latest_bid']
        end_date = datetime.strptime(art.auction['end_date'], "%Y-%m-%d")
        date = datetime.now()
        if latest_bid ==  None or latest_bid < bid:
            if bid<=art.price:
                messages.error(request, "Your bid must be higher than the current price!")
                return redirect(f'/show_art/{art.id}/')
            elif date <= end_date:
                user = User.objects.get(username=request.session["username"])
                offer = {'user_id': user.id, 'date': date.strftime("%Y-%m-%d"), 'bid': bid}
                art.auction['latest_bid'] = bid
                art.auction['offers'].append(offer)
                art.save()

                # Sending Mail
                context = {'user': user, 'artist': art.artist, 'art': art, 'last_bid': latest_bid}
                message = render_to_string('email3.html', context) 
                subject = f'{user.username} is has placed a bid in your Art!'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [art.artist.email,]
                send_mail(subject, message, email_from, recipient_list)

                messages.error(request, "Your bid was saved. You will be contacted by the artist.")
                return redirect(f'/show_art/{art.id}/')
            else:
                messages.error(request, "Sorry, bidding closed!")
                return redirect(f'/show_art/{art.id}/')

        else:
            messages.error(request, "Your bid must be higher than the current price!")
            return redirect(f'/show_art/{art.id}/')

@csrf_exempt
def like_art(request):
    if request.method == "POST":
        user = User.objects.get(username=request.session["username"])
        art = Post.objects.get(id=request.POST.get('art_id'))
        if int(request.POST.get('action')) == 1:
            like = Like(user=user, post=art)
            like.save()
        else:
            like = Like.objects.get(user=user, post=art)
            like.delete()

        no_of_likes = Like.objects.filter(post=art).count()
        return JsonResponse({'no_of_likes': no_of_likes})

@csrf_exempt
def comment(request):
    if request.method == "POST":
        user = User.objects.get(username=request.session["username"])
        art = Post.objects.get(id=request.POST.get('art'))
        message = request.POST.get("comment")
        comment = Comment(user=user, post=art, text=message)
        comment.save()
        return redirect(f'/show_art/{art.id}/')

def delete_post(request, art_id):
    if request.method == "GET":
        art = Post.objects.get(id=art_id)
        art.delete()
        messages.error(request, "Art has been deleted!")
        return redirect("dashboard")

def send_email(request):
    if request.method == "POST":
        art = Post.objects.get(id=request.POST.get('art'))
        user = User.objects.get(username=request.session["username"])
        sale_type = request.POST.get('sale_type')
        if sale_type == "2":
            context = {'user': user, 'artist': art.artist, 'art': art}
            message = render_to_string('email1.html', context)
        elif sale_type == "3":
            context = {'user': user, 'artist': art.artist, 'art': art}
            message = render_to_string('email2.html', context)

        subject = f'{user.username} is interested in your Art!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [art.artist.email,]
        send_mail(subject, message, email_from, recipient_list)


        messages.error(request, "The Artist will be notified of your request!") 
        return redirect(f'/show_art/{art.id}/')