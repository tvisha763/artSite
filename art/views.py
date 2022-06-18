from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
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

    return render(request, 'signup.html')

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

           
            salted_password = bcrypt.hashpw(password, saved_salt)
            if salted_password == saved_hashed_pass:
                return redirect('home')
            else:
                messages.error(request, "Your password is incorrect.")
                return redirect('login')

        else:
            messages.error(request, "An account with this email does not exist. Please sign up.")
            return redirect('login')

    return render(request, 'login.html')

def home(request):
    user = User.objects.get(username=request.session["username"])
    return render(request, 'home.html')

def post(request):
    user = User.objects.get(username=request.session["username"])
    return render(request, 'postArtwork.html')