from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager  
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractBaseUser, PermissionsMixin):
    ACCOUNT_TYPE_CHOICES = ( 
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100) 
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)  
    country = models.CharField(max_length=50)
    country_code = models.CharField(max_length=10) 
    state = models.CharField(max_length=50)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)  
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()  

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'account_type']

    def __str__(self):
        return self.email
    
    def tokens(self):
        try:
            refresh = RefreshToken.for_user(self)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        except Exception as e:
            print(f"Token generation error: {e}")
            raise AuthenticationFailed('Failed to generate authentication tokens.')
  
        
        

class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    code  = models.CharField(max_length=6,unique=True)
      
    def __str__(self):
        return f"{self.user.first_name}-passcode" 
       
          
          