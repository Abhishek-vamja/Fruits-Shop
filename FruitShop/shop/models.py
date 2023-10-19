"""
Models for shop app.
"""

from django.db import models
from core.models import BaseModel
from django.conf import settings
import datetime


class Category(BaseModel):
    """Category objects."""
    title = models.CharField(max_length=255, blank=False)
    slug = models.SlugField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Categorie"

    def __str__(self) -> str:
        return self.title


class Product(BaseModel):
    """Product objects."""   
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category,related_name="product",on_delete=models.CASCADE)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='img/prod',null=True)
    available = models.BooleanField(default=True)
    slug = models.SlugField()

    percent_off = models.CharField(max_length=10, null=True)
    is_time_limited = models.BooleanField(default=False)
    discount_price = models.FloatField(null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '{}, {}'.format(self.title,self.category)


DEAL_OF = (
    ('Day', 'Day'),
    ('Month', 'Month'),
    ('Year', 'Year')
)

class OfferProduct(Product):
    """Limited time offer."""
    deal_of = models.CharField(max_length=255, choices=DEAL_OF, default='Month')
    date = models.CharField(max_length=255, null=True)

    def __str__(self):
        return str(self.title)

class Cart(BaseModel):
    """Cart objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return str(self.user)


class Checkout(BaseModel):
    """Checkout objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()
    mobile = models.CharField(max_length=10)
    note = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return str(self.user)


STATUS_CHOICE = (
    ('Order Pending','Order Pending'),
    ('Confirmed','Confirmed'),
    ('Packed','Packed'),
    ('Shipped','Shipped'),
    ('Outer Delivery','Outer Delivery'),
    ('Delivered','Delivered'),
)


PAYMENT = (
    ('Online','Online'),
    ('COD','COD')
)

class OrderPlaced(BaseModel):
    """OrderPlaced objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50,choices=STATUS_CHOICE,default='Order Pending')
    paid = models.BooleanField(default=False)
    payment = models.CharField(max_length=255,choices=PAYMENT,default='COD')
    ordered_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ordered_date']
    
    def __str__(self) -> str:
        return f"Order {self.id} by {self.user}"
