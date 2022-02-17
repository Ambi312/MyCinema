from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number must be provided')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.create_activation_code()
        user.save(using=self.db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number must be provided')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self.db)
        return user


class CustomUser(AbstractUser):
    phone_number = PhoneNumberField(unique=True)
    username = models.CharField(max_length=155, unique=True)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=6, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    def create_activation_code(self):
        code = get_random_string(length=6, allowed_chars='0123456789')
        self.activation_code = code

    def __str__(self):
        return f'{self.username} {self.phone_number}'
