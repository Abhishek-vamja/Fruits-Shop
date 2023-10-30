"""
User admin site.
"""

from django.contrib import admin
from user.models import *

admin.site.register(User)
admin.site.register(Profile)