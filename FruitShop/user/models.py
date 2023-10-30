"""
Models for users.
"""

from django.db import models
from django.conf import settings
from core.models import BaseModel
from django.contrib.auth.models import (
    AbstractBaseUser , PermissionsMixin , BaseUserManager
    )


class UserManager(BaseUserManager):
    """Manager for user."""

    def create_user(self,email,password=None,**extra_fields):
        """Create,save and return new user."""

        if not email:
            raise ValueError('User must have an email address.')
        
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self,email,password):
        """Create and return a new superuser"""
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser,PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255,unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Profile(BaseModel):
    """User profile."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    otp = models.CharField(max_length=4)

    def __str__(self) -> str:
        return str(self.user)