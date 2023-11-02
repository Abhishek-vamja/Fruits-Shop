from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import logout, login, authenticate
from datetime import datetime, time
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from user.models import *
from shop.models import Address
import http.client
from django.views.decorators.csrf import csrf_exempt


class UserAuth:
    """Handle user authentication"""
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
            UserAuth.send_otp(mobile , otp)
            request.session['mobile'] = mobile
            return redirect('login_otp')        
        return render(request,'user/login.html')

    # NOT working as expected...
    def resend_otp(request):
        if request.method == 'POST':
            mobile = request.POST.get('mobile')
            user = Profile.objects.filter(mobile=mobile).first()
            if user:
                otp = str(random.randint(1000, 9999))
                user.otp = otp
                user.save()
                UserAuth.send_otp(mobile, otp)
                request.session['mobile']=mobile
                return redirect('login_otp')
            else:
                return redirect('login_otp')
            
        return render(request, 'user/verify_otp.html')

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


    # Not working as expected...
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
            UserAuth.send_otp(mobile, otp)
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


"""
User Profile session.
"""

class UserAccounts(LoginRequiredMixin):
    """Handle user account."""
    def user_account(request):
        """User detail."""
        greeting = get_time_of_day_greeting()

        context = {
            'greeting': greeting
        }
        return render(request, 'user/profile.html', context)
    
    class UserAddress:
        """HAndle address of account."""
        def user_address(request):
            """Users Address."""
            address = Address.objects.filter(user=request.user)
            context = {
                'address': address
            }
            return render(request, 'user/user_address.html', context)


        def add_user_address(request):
            """Add new address for user."""
            if request.method == "POST":
                country = request.POST.get('country')
                full_name = request.POST.get('full_name')
                mobile = request.POST.get('mobile')
                pincode = request.POST.get('pincode')
                flat =  request.POST.get('flat')
                area =  request.POST.get('area')
                landmark = request.POST.get('landmark')
                city =  request.POST.get('city')
                state = request.POST.get('state')
                user = request.user

                address = Address(
                    user=user, full_name=full_name, mobile=mobile,
                    pincode=pincode, flat=flat, area=area,
                    landmark=landmark, city=city, state=state, country=country
                )
                address.save()
                messages.success(request, 'Address added successfully!!')
                return redirect('user-address')
            
            return render(request, 'user/user_add_address.html', locals())


        def user_change_address(request,address_id):
            """Change address as needed."""
            address = get_object_or_404(Address, id=address_id)

            if request.method == 'POST':
                country = request.POST.get('country')
                full_name = request.POST.get('full_name')
                mobile = request.POST.get('mobile')
                pincode = request.POST.get('pincode')
                flat =  request.POST.get('flat')
                area =  request.POST.get('area')
                landmark = request.POST.get('landmark')
                city =  request.POST.get('city')
                state = request.POST.get('state')
                default_id = request.POST.get('default')
                user = request.user

                """
                Update the fields of the address object.
                """
                if default_id:
                    set_as_default = Address.objects.get(user=user,id=default_id)
                    set_as_default.default = True
                    set_as_default.save()

                    Address.objects.filter(user=user).exclude(id=default_id).update(default=False)
                    Address.objects.filter(id=default_id).update(
                        country=country,full_name=full_name,mobile=mobile,pincode=pincode,
                        flat=flat,area=area,landmark=landmark,city=city,state=state,user=user)
                    messages.success(request, 'Address change successfully!!')
                    return redirect('user-address')
                else:
                    Address.objects.filter(id=address_id).update(
                        country=country,full_name=full_name,mobile=mobile,pincode=pincode,
                        flat=flat,area=area,landmark=landmark,city=city,state=state,user=user)
                    messages.success(request, 'Address change successfully!!')
                    return redirect('user-address')
            
            context = {
                'obj': address
            }
            return render(request, 'user/user_change_address.html', context)


        def make_default_address(request,address_id):
            """Make default address"""
            try:
                address_to_set_default = Address.objects.get(user=request.user,id=address_id)
                address_to_set_default.default = True
                address_to_set_default.save()

                """
                Set all other addresses as non-default.
                """
                Address.objects.filter(user=request.user).exclude(id=address_id).update(default=False)
                messages.success(request, 'Changed default address successfully!!')
                return redirect('user-address')
            except Address.DoesNotExist:
                
                print('EEEEEEEE')    


        def remove_user_address(request, address_id):
            """Remove user address."""
            address = Address.objects.get(id=address_id)
            address.delete()
            messages.success(request ,'Remove address successfully!!')
            return redirect('user-address')


def get_time_of_day_greeting():
    now = datetime.now()
    current_time = now.time()
    
    if current_time < time(12, 0):
        return "Good morning"
    elif current_time < time(17, 0):
        return "Good afternoon"
    else:
        return "Good evening"