from django.urls import path
from .views import LoginUserView, RegisterUser



urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
   
]