"""
Shop admin site.
"""

from django.contrib import admin
from shop.models import *


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Checkout)
admin.site.register(OrderPlaced)