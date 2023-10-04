"""
Models for shop app.
"""

from django.db import models
from core.models import BaseModel
from django.conf import settings


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
