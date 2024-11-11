from django.urls import path
from . import views

urlpatterns = [
    path('register_user/', views.register_user, name='register_user'),
    path('verify-email/', views.verify_user_email, name='verify-email'),  # Email verification
    path('login/', views.login_user, name='login-user'),# User login
    path('set-new-password/', views.set_new_password, name='set-new-password'),  # Set new password
    path('password-reset-request/', views.password_reset_request, name='password-reset-request'),  # Password reset request
    path('password-reset-confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password-reset-confirm'),  # Password reset confirmation
    
]