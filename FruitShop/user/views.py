from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import logout, login, authenticate
from datetime import datetime, time
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
import random
from user.models import *
from shop.models import *
import http.client
import requests
from django.views.decorators.csrf import csrf_exempt


class UserAuth:
    """
    Handle user authentication.
    """


    def send_otp(mobile , otp):
        """
        Log the user out and redirect to the shop page.

        This function logs the user out of their session and redirects them to the shop page.
        """
        auth_key = settings.AUTH_KEY
        url = f"https://control.msg91.com/api/v5/otp?mobile=91{mobile}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authkey": auth_key
        }

        response = requests.post(url, headers=headers)
        
        # Check the response status
        if response.status_code == 200:
            print("OTP sent successfully")
        else:
            print(f"Failed to send OTP. Status code: {response.status_code}")
            print(response.text)

    def user_logout(request):
        """        
        Log the user out and redirect to the shop page.        

        This function logs the user out of their session and redirects them to the shop page.
        """
        logout(request)
        return redirect('index')

    def login_attempt(request):
        """
        Handle user login attempts and OTP generation.

        This function handles user login attempts, generates an OTP, and sends it to the user's mobile number.
        If the user is not found, it displays a message on the login page.
        """
        if request.method == 'POST':
            mobile = request.POST.get('mobile')
            
            user = Profile.objects.filter(mobile=mobile).first()
            
            if user is None:
                context = {'message' : 'Please check entered Mobile Number !!' , 'class' : 'danger' }
                return render(request,'user/login.html' , context)
            
            otp = str(random.randint(1000 , 9999))
            user.otp = otp
            user.save()
            UserAuth.send_otp(mobile , otp)
            request.session['mobile'] = mobile
            return redirect('login_otp')        
        return render(request,'user/login.html')

    def resend_otp(request):
        """
        Resend the OTP to the user's mobile number.

        This function allows the user to request a resend of the OTP to their mobile number.
        It checks if the user exists and resend the OTP accordingly.
        """
        mobile = request.session['mobile']
        print(mobile)
        user = Profile.objects.filter(mobile=mobile).first()
        if user:
            otp = str(random.randint(1000, 9999))
            user.otp = otp
            try:
                if user.otp_attempt == 0:
                    messages.warning(request, 'You have not attempt !!')
                else:
                    user.otp_attempt -= 1

            except Exception as e:
                print(e, 'EEEEE')

            user.save()
            UserAuth.send_otp(mobile, otp)
            return redirect('login_otp')
        else:
            return redirect('login_otp')

    @csrf_exempt
    def login_otp(request):
        """
        Verify the OTP and log the user in.

        This function verifies the OTP entered by the user and logs them in if it matches the stored OTP.
        If the OTP is incorrect, it displays an error message.
        """
        mobile = request.session['mobile']
        context = {'mobile':mobile}
        if request.method == 'POST':
            otp = request.POST.get('otp')
            profile = Profile.objects.filter(mobile=mobile).first()
            
            if otp == profile.otp:
                user = User.objects.get(id = profile.user.id)
                login(request , user)
                profile.otp_attempt = 3
                profile.save()
                return redirect('index')
            else:
                context = {'message' : 'Wrong OTP !!' , 'class' : 'danger','mobile':mobile }
                return render(request,'user/verify_otp.html' , context)
        
        return render(request,'user/verify_otp.html' , context)

    def login_email(request):
        """
        Log in the user using email and password.

        This function attempts to log in the user by authenticating the provided email and password. If the authentication is successful,
        the user is logged in and redirected to the homepage. If the authentication fails, an error message is displayed.
        """
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                print('login')
                login(request, user)
                return redirect('index')
            else:
                print('In Elseeee')
                context = {
                    'message': 'email and password are not valid !!',
                    'class': 'danger',
                }
                return render(request, 'user/login_email.html', context)
            
        return render(request, 'user/login_email.html')

    def register(request):
        """
        Register a new user.

        This function handles user registration. It checks if the user and profile with the provided email and mobile number
        already exist. If not, it creates a new user and sends an OTP to the user's mobile number for verification.
        """
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
                
            user = User.objects.create_user(email = email , name = name, password = password)
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
        """
        Verify the OTP and log the user in after registration.

        This function verifies the OTP entered during the registration process and logs the user in if it matches the stored OTP.
        If the OTP is incorrect, it displays an error message.
        """
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
    """
    This class handles user accounts and provides methods,
    for managing user details and addresses.
    """


    def user_account(request):
        """
        Renders the user's account details.
        """
        greeting = get_time_of_day_greeting()
        context = {
            'greeting': greeting
        }
        return render(request, 'user/profile.html', context)
    
    class UserAddress:
        """
        This nested class handles user addresses within the user account.
        """


        def user_address(request):
            """
            Renders the list of user addresses.
            """
            address = Address.objects.filter(user=request.user)
            context = {
                'address': address
            }
            return render(request, 'user/user_address.html', context)

        def add_user_address(request):
            """
            Add a new address for user.
            """
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

                if Address.objects.filter(user=user).count() == 0:
                    address.default = True
                else:
                    address.default = False
                address.save()

                messages.success(request, 'Address added successfully!!')
                return redirect('user-address')
            
            return render(request, 'user/user_add_address.html', locals())

        def user_change_address(request,address_id):
            """
            Allows the user to change an existing address.
            """
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
                
                # Update the fields of the address object.
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
            """
            Sets a user's address as the default address.
            """
            try:
                address_to_set_default = Address.objects.get(user=request.user,id=address_id)
                address_to_set_default.default = True
                address_to_set_default.save()
                
                # Set all other addresses as non-default.
                Address.objects.filter(user=request.user).exclude(id=address_id).update(default=False)
                messages.success(request, 'Changed default address successfully!!')
                return redirect('user-address')
            
            except Address.DoesNotExist:
                print('EEEEEEEE')    

        def remove_user_address(request, address_id):
            """
            Remove user's address.
            """
            address = Address.objects.get(id=address_id)
            address.delete()
            messages.success(request ,'Remove address successfully!!')
            return redirect('user-address')

    class UserProfile:
        """
        Handle user's profile.
        """


        def get_user_profile(request):
            """
            Retrieves and renders the user's profile information.
            """
            user_profile = Profile.objects.get(user=request.user)
            context = {
                'profile': user_profile
            }
            return render(request , 'user/user_profile.html', context)        

        def change_user_name(request, user_id):
            """
            Allows the user to change their name.
            """
            profile = get_object_or_404(Profile, id=user_id)

            if request.method == 'POST':              
                user_name = request.POST.get('name')                
                profile.user.name = user_name
                profile.user.save()
                
                messages.success(request, 'Name changed!!')
                return redirect('user-profile')
            
            context = {
                'profile': profile
            }

            return render(request, 'user/change_name.html', context)


# ...ADMIN...

class Dashboard(LoginRequiredMixin):    

    @permission_required('is_superuser')
    def get_dashboard(request):
        order_obj = OrderPlaced.objects.exclude(status='Delivered')
        complete_order_obj = OrderPlaced.objects.filter(status='Delivered')
        contact_obj = Contact.objects.filter(read=False)
        user_obj = User.objects.all()
        product_obj = Product.objects.all()
        news_obj = News.objects.all()

        amount = 0
        for i in complete_order_obj:
            value = i.price
            amount = value + amount

        total_earning = amount

        context = {
            'orders': order_obj,
            'users': user_obj,
            'complete_order': complete_order_obj,
            'total_earning': total_earning,
            'contact': contact_obj,
            'product': product_obj,
            'news': news_obj,
        }
        return render(request, 'dash/index.html', context)

    @permission_required('is_superuser')
    def get_users(request):
        users_obj = Profile.objects.annotate(
            num_orders=Count('user__orderplaced', filter=Q(user__orderplaced__status='Delivered'), distinct=True),
            num_addresses=Count('user__address', distinct=True),
            num_comments=Count('user__comment', distinct=True)
        )

        # Number of items to display per page
        items_per_page = 9  # Adjust as needed

        # Paginate the user data
        paginator = Paginator(users_obj, items_per_page)
        page = request.GET.get('page', 1)

        try:
            users_data = paginator.page(page)
        except PageNotAnInteger:
            users_data = paginator.page(1)
        except EmptyPage:
            users_data = paginator.page(paginator.num_pages)

        context = {
            'users_data': users_data,
        }
        return render(request, 'dash/all_user.html', context)

    @permission_required('is_superuser')
    def delete_user(request, user_id):
        user_obj = User.objects.get(id=user_id)
        user_obj.delete()
        return redirect('all-users')

    @permission_required('is_superuser')
    def get_products(request):
        all_products = Product.objects.all()
        category_obj = Category.objects.all()

        # Number of items to display per page
        items_per_page = 15  # Adjust as needed

        # Paginate the user data
        paginator = Paginator(all_products, items_per_page)
        page = request.GET.get('page', 1)

        try:
            product_data = paginator.page(page)
        except PageNotAnInteger:
            product_data = paginator.page(1)
        except EmptyPage:
            product_data = paginator.page(paginator.num_pages)

        context = {
            'products': product_data,
            'category': category_obj,
        }
        return render(request, 'dash/all_products.html', context)

    @permission_required('is_superuser')
    def add_products(request):
        category_obj = Category.objects.all()

        # Add Product Login...
        if request.method == 'POST':
            title = request.POST.get('title')
            category = request.POST.get('category')
            price = request.POST.get('price')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            available = request.POST.get('available') == 'on'
            slug = request.POST.get('slug')
            percent_off = request.POST.get('percent_off')
            is_time_limited = request.POST.get('is_time_limited') == 'on'
            discount_price = request.POST.get('discount_price')
            deal_of = request.POST.get('deal_of')
            date = request.POST.get('date')

            category_instance = get_object_or_404(Category, title=category)
            discount_price = float(discount_price) if discount_price else None

            products_obj = Product(
                title=title, category=category_instance, price=price, description=description,
                image=image, available=available, slug=slug, percent_off=percent_off,
                is_time_limited=is_time_limited, discount_price=discount_price,
                deal_of=deal_of, date=date
            )
            
            products_obj.save()
            messages.success(request, 'Product add successfully!!')

        context = {
            'category': category_obj,
        }
        return render(request, 'dash/add_products.html', context)

    @permission_required('is_superuser')
    def edit_products(request, product_id):
        product_obj = get_object_or_404(Product, id=product_id)

        if request.method == 'POST':
            title = request.POST.get('title')
            category = request.POST.get('category')
            price = request.POST.get('price')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            available = request.POST.get('available') == 'on'
            slug = request.POST.get('slug')
            percent_off = request.POST.get('percent_off')
            is_time_limited = request.POST.get('is_time_limited') == 'on'
            discount_price = request.POST.get('discount_price')
            deal_of = request.POST.get('deal_of')
            date = request.POST.get('date')

            category_instance = get_object_or_404(Category, title=category)
            discount_price = float(discount_price) if discount_price else None

            upload_path = 'img/prod'
            if image:
                file_name = default_storage.save(f'{upload_path}/{image.name}', ContentFile(image.read()))
                
                Product.objects.filter(id=product_id).update(
                    title=title, category=category_instance, price=price, description=description,
                    image=file_name, available=available, slug=slug, percent_off=percent_off,
                    is_time_limited=is_time_limited, discount_price=discount_price, deal_of=deal_of,
                    date=date
                )
            else:
                Product.objects.filter(id=product_id).update(
                    title=title, category=category_instance, price=price, description=description,
                    available=available, slug=slug, percent_off=percent_off,
                    is_time_limited=is_time_limited, discount_price=discount_price, deal_of=deal_of,
                    date=date
                )
            messages.success(request, f'Product {title} change successfully!!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    @permission_required('is_superuser')
    def delete_product(request, product_id):
        product_obj = Product.objects.get(id=product_id)
        product_obj.delete()
        messages.success(request, 'Product delete successfully!!')
        return redirect('all-products')

    @permission_required('is_superuser')
    def get_category(request):
        category_obj = Category.objects.all()

        context = {
            'category': category_obj,
        }
        return render(request, 'dash/all_category.html', context)

    @permission_required('is_superuser')
    def add_category(request):
        
        if request.method == 'POST':
            title = request.POST.get('title')
            slug = request.POST.get('slug')

            category_obj = Category(title=title, slug=slug)
            category_obj.save()
            messages.success(request, f'Category {title} added successfully!!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        return render(request, 'dash/add_category.html')

    @permission_required('is_superuser')
    def edit_category(request, category_id):

        if request.method == 'POST':
            title = request.POST.get('title')
            slug = request.POST.get('slug')

            Category.objects.filter(id=category_id).update(title=title,slug=slug)
            messages.success(request, f'Category {title} change successfully!!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    @permission_required('is_superuser')
    def delete_category(request, category_id):

        category_obj = Category.objects.filter(id=category_id)
        category_obj.delete()
        messages.info(request, 'Category deleted successfully!!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def get_time_of_day_greeting():
    """
    Determines the time of day and returns an appropriate, 
    greeting message (e.g., "Good morning," "Good afternoon," or "Good evening").
    """
    now = datetime.datetime.now()
    current_time = now.time()
    print(current_time)

    if current_time < time(12, 0):
        return "Good morning"
    elif current_time < time(17, 0):
        return "Good afternoon"
    else:
        return "Good evening"