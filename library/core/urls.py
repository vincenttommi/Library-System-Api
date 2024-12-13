from django.urls import path
from .views import BorrowBook, Creating_BookView, DeleteBook, EditBook, ListingBooks,LoginUserView, LogoutUserView, PasswordResetConfirm, PasswordResetRequest, RegisterUser, ReturnBook, SetNewPassword, VerifyuserEmail



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
    path('edit/<int:id>/', EditBook.as_view(), name='edit-book'),
    path('delete_book/<int:book_id>/', DeleteBook.as_view(),name='delete_book'),
    path('borrow/', BorrowBook.as_view(), name='borrow-book'),
    path("return-book/",ReturnBook.as_view(), name='returning book')
    
]