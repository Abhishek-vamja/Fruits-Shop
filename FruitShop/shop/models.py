"""
Models for shop app.
"""

from django.db import models
from core.models import BaseModel
from django.conf import settings
import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_date_format(value):
    try:
        # Attempt to parse the date using the specified format
        datetime.datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        # If parsing fails, raise a validation error
        raise ValidationError(_('Invalid date format. Use YYYY-MM-DD.'), code='invalid_date_format')

class Category(BaseModel):
    """Category objects."""
    title = models.CharField(max_length=255, blank=False)
    slug = models.SlugField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Categorie"

    def __str__(self) -> str:
        return self.title

DEAL_OF = (
    ('Day', 'Day'),
    ('Month', 'Month'),
    ('Year', 'Year')
)

class Contact(BaseModel):
    """Contact objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.user} contact you..'


class Product(BaseModel):
    """Product objects."""   
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category,related_name="product",on_delete=models.CASCADE)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='img/prod',null=True)
    available = models.BooleanField(default=True)
    slug = models.SlugField()

    percent_off = models.CharField(max_length=10, null=True, blank=True)
    is_time_limited = models.BooleanField(default=False)
    discount_price = models.FloatField(null=True, blank=True)
    deal_of = models.CharField(max_length=255, choices=DEAL_OF, default='Month')
    date = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '{}, {}'.format(self.title,self.category)


class Cart(BaseModel):
    """Cart objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return str(self.user)


class Address(BaseModel):
    """Address objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=10)
    pincode = models.CharField(max_length=6)
    flat = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255, default=1)
    default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-default']

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
    product = models.ManyToManyField(Product)
    quantity = models.CharField(max_length=255,blank=True,null=True)
    price = models.FloatField(default=0)
    discount_price = models.FloatField(default=0)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, default="")
    status = models.CharField(max_length=50,choices=STATUS_CHOICE,default='Confirmed')
    paid = models.BooleanField(default=False)
    payment_mode = models.CharField(max_length=255,choices=PAYMENT,default='COD')
    ordered_date = models.DateTimeField(auto_now_add=True,null=True)
    delivered_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-ordered_date']

    def __str__(self) -> str:
        return f"Order {self.id} by {self.user}"


class Coupon(BaseModel):
    """Coupon objects."""
    code = models.CharField(max_length=15, unique=True)
    discount_value = models.FloatField()
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Coupon Code {self.code}"


class News(BaseModel):
    """News objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='img/news',null=True)
    description = models.TextField()

    def __str__(self) -> str:
        return f'{self.user.name}, {self.title}'


class Comment(BaseModel):
    """Comment objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    message = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Comment by {self.user} on {self.news.title}'


class Quote(BaseModel):
    """Quote objects."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    quote_writer = models.CharField(max_length=20, null=True)
    quote = models.TextField()

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"Quote by {self.user}"