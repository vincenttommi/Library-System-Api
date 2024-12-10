from django.urls import path
from .views import Creating_BookView, ListingBooks,LoginUserView, LogoutUserView, PasswordResetConfirm, PasswordResetRequest, RegisterUser, SetNewPassword, VerifyuserEmail



urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('verify/', VerifyuserEmail.as_view(), name='verify'),
    path('password-reset-request/', PasswordResetRequest.as_view(), name='verify'),
    path('password-reset-confrim/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='set-new-password'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('creating-book/', Creating_BookView.as_view(), name='creating'),
    path('listing-book/', ListingBooks.as_view(), name ='listing'),
    path('book/<int:id>/', ListingBooks.as_view(), name ='retrieve-book'),
]