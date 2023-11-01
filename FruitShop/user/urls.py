"""
Url mapping for user.
"""
from django.urls import path
from user.views import *

urlpatterns = [
    # USER AUTHENTICATION...
    path('' , UserAuth.login_attempt , name="login"),
    path('register/' , UserAuth.register , name="register"),
    path('otp/' , UserAuth.otp , name="otp"),
    path('login-otp/', UserAuth.login_otp , name="login_otp"),
    path('login-email/', UserAuth.login_email, name='login-email'),
    path('logout/', UserAuth.user_logout, name='logout'),


    # USER ACCOUNT...
    path('your-account/', UserAccounts.user_account, name='user-account'),
    
    # USER ACCOUNT >> USER ORDERS...
    # Make Soon..


    # USER ACCOUNT >> LOGIN & SECURITY...
    # Make Soon..


    # USER ACCOUNT >> USER ADDRESS...
    path('your-address/', UserAccounts.UserAddress.user_address, name='user-address'),
    path('new-address/', UserAccounts.UserAddress.add_user_address, name='new-address'),
    path('change-address/<uuid:address_id>/', UserAccounts.UserAddress.user_change_address, name='change-address'),
    path('make-default/<uuid:address_id>/', UserAccounts.UserAddress.make_default_address, name='make-default'),
    path('remove-address/<uuid:address_id>/', UserAccounts.UserAddress.remove_user_address, name='remove-address')
    

    # USER ACCOUNT >> CONTACT...
    # Make Soon..
]