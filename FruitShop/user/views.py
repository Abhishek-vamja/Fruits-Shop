from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import logout, login, authenticate
from django.views.generic import View
from datetime import datetime, time
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from user.models import *
import http.client
from django.views.decorators.csrf import csrf_exempt


def send_otp(mobile , otp):
    """
    Send otp to user mobile.
    """
    print("FUNCTION CALLED")
    conn = http.client.HTTPSConnection("api.msg91.com")
    authkey = settings.AUTH_KEY 
    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authkey": authkey
    }
    url = "https://control.msg91.com/api/v5/otp?mobile=91"+mobile
    conn.request("GET", url , headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data)
    return None


def user_logout(request):
    """Logout user."""
    logout(request)
    return redirect('/shop/')


def login_attempt(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        
        user = Profile.objects.filter(mobile=mobile).first()
        
        if user is None:
            context = {'message' : 'User not found' , 'class' : 'danger' }
            return render(request,'user/login.html' , context)
        
        otp = str(random.randint(1000 , 9999))
        user.otp = otp
        user.save()
        send_otp(mobile , otp)
        request.session['mobile'] = mobile
        return redirect('login_otp')        
    return render(request,'user/login.html')

@csrf_exempt
def login_otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()
        
        if otp == profile.otp:
            user = User.objects.get(id = profile.user.id)
            login(request , user)
            return redirect('index')
        else:
            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'user/verify_otp.html' , context)
    
    return render(request,'user/verify_otp.html' , context)

# Not working properly..
def login_email(request):
    """Login with email and password."""
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,username=email, password=password)
        print(user)

        if user is not None:
            print('login')
            login(request, user)
            return redirect('index')
        else:
            print('In Elseeee')
            context = {
                'message': 'email and password are not valid',
                'class': 'danger',
            }
            return render(request, 'user/login_email.html', context)
        
    return render(request, 'user/login_email.html')


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        
        check_user = User.objects.filter(email = email).first()
        check_profile = Profile.objects.filter(mobile = mobile).first()
        
        if check_user or check_profile:
            context = {'message' : 'User already exists' , 'class' : 'danger' }
            return render(request,'user/register.html' , context)
            
        user = User(email = email , name = name, password = password)
        user.save()
        otp = str(random.randint(1000 , 9999))
        profile = Profile(user = user , mobile=mobile , otp = otp) 
        profile.save()
        send_otp(mobile, otp)
        request.session['mobile'] = mobile
        return redirect('otp')
    return render(request,'user/register.html')

@csrf_exempt
def otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()
        
        if otp == profile.otp:
            user = User.objects.get(id = profile.user.id)
            login(request , user)
            return redirect('index')
        else:
            print('Wrong')
            
            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'user/verify_otp.html' , context)
            
        
    return render(request,'user/verify_otp.html' , context)


"""User Profile session."""

def user_account(request):
    """User detail."""
    greeting = get_time_of_day_greeting()

    context = {
        'greeting': greeting
    }
    return render(request, 'user/profile.html', context)


def user_address(request):
    """Users Address."""
    return render(request, 'user/user_address.html')


def get_time_of_day_greeting():
    now = datetime.now()
    current_time = now.time()
    
    if current_time < time(12, 0):
        return "Good morning"
    elif current_time < time(17, 0):
        return "Good afternoon"
    else:
        return "Good evening"