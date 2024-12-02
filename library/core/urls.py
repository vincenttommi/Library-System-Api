from django.urls import path
from .views import LoginUserView, LogoutUserView, PasswordResetConfirm, PasswordResetRequest, RegisterUser, SetNewPassword, VerifyuserEmail



urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('verify/', VerifyuserEmail.as_view(), name='verify'),
    path('password-reset-request/', PasswordResetRequest.as_view(), name='verify'),
    path('password-reset-confrim/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
  
]