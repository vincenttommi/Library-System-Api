from django.urls import path
from .views import LoginUserView, RegisterUser, VerifyuserEmail



urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('verify/', VerifyuserEmail.as_view(), name='verify'),
   
    
    
    
    
    

   
]