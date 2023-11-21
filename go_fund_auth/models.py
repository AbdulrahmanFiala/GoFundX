from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import datetime


# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)
#     email_confirmed = models.BooleanField(default=False)
#     mobile_phone = models.CharField(max_length=15, unique=True)
#     profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
#     birthdate = models.DateField(null=True, blank=True)
#     facebook_profile = models.URLField(null=True, blank=True)
#     country = models.CharField(max_length=50, null=True, blank=True)
#     activation_sent_date = models.DateTimeField(default=datetime.now)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['mobile_phone']

#     def __str__(self):
#         return self.email


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, mobile_phone, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, mobile_phone=mobile_phone, first_name=first_name, last_name=last_name,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, mobile_phone, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, mobile_phone, first_name, last_name, password, **extra_fields)

    def create_superuser(self, email, mobile_phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, mobile_phone, first_name='', last_name='', password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    email_confirmed = models.BooleanField(default=False)
    mobile_phone = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    facebook_profile = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    activation_sent_date = models.DateTimeField(default=datetime.now)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile_phone']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
