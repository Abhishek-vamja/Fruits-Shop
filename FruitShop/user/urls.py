"""
Url mapping for user.
"""
from django.urls import path
from user.views import *

urlpatterns = [
    path('' , login_attempt , name="login"),
    path('register/' , register , name="register"),
    path('otp/' , otp , name="otp"),
    path('login-otp/', login_otp , name="login_otp"),
    path('login-email/', login_email, name='login-email'),
    path('logout/', user_logout, name='logout'),


    path('your-account/', user_account, name='user-account'),
    path('your-address/', user_address, name='user-address'),
    
]