from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed


class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'), 
        ('student', 'Student'),
        ('resident', 'Resident'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username}"

    def save(self, *args, **kwargs):
        # Clear out fields based on user type
        if self.role == 'student':
            self.address = None
            self.phone_number = None
            self.estate = None
        elif self.role == 'resident':
            self.school_name = None
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return self.username

    def tokens(self):
        try:
            refresh = RefreshToken.for_user(self)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        except Exception:
            raise AuthenticationFailed('Error generating tokens')


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateTimeField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    BOOK_STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
    ]
    status = models.CharField(max_length=10, choices=BOOK_STATUS_CHOICES, default='available')

    def __str__(self):
        return self.title


class BorrowingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowing_history')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowing_records')
    borrowed_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    renewal_count = models.PositiveIntegerField(default=0)
    fine = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def calculate_fine(self):
        if not self.return_date and (timezone.now().date() > self.return_date):
            overdue_days = (timezone.now().date() - self.return_date).days
            if overdue_days > 0:
                self.fine = overdue_days * 100
            else:
                self.fine = 0
        else:
            self.fine = 0
        self.save()
        return self.fine


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('cancelled', 'Cancelled')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
     
    def __str__(self):
        return f"{self.user.username} reserved {self.book.title}"


class Fine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fines")
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('Sent', 'Sent'), ('Read', 'Read')])

    def __str__(self):
        return f"Notification for {self.user.username}"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Feedback from {self.user.username}"



class Admin(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE,related_name='admin')
    identification_photo = models.ImageField(upload_to='admin_photos')
    created_at = models.DateTimeField(auto_now_add=True)

   


    def __str__(self):
        return f"Admin:{self.user.username}"
    


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='students')
    school_name  = models.CharField(max_length=100)
    school_registration_number = models.CharField(max_length=20, unique=True)
    identification_photo = models.ImageField(upload_to='student_photos/')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Student:{self.user.username}"
    



class Resident(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='resident')
    identification_photo = models.ImageField(upload_to='admin_photos')
    address  = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    estate = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
                                                                                                                                                                                                                                                                                                        

    def __str__(self):
        return f"Resident:{self.username}"
    
         