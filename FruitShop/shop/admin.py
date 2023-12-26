"""
Shop admin site.
"""

from django.contrib import admin
from shop.models import *


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(OrderPlaced)
admin.site.register(Coupon)
admin.site.register(Contact)
admin.site.register(News)
admin.site.register(Comment)
admin.site.register(Quote)
admin.site.register(Review)