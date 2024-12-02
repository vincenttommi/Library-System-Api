from  rest_framework.views import APIView
from core.serializers import UserRegisterSerializer,LoginSerializer
from core.utils import send_code_to_user
from rest_framework.response import Response
from rest_framework import status
from .models import OneTimePassword,User



class RegisterUser(APIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            # Attempt to send email
            try:
                send_code_to_user(user['email'])
            except Exception as e:
                # Handle email sending failure gracefully
                print(f"Failed to send email: {e}")
                return Response({"error": "Email sending failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Email was sent successfully, return response
            return Response({
                'data': user,
                'message': f'Hi {user["name"]}, thanks for signing up! A passcode has been sent to your email.'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginUserView(APIView):
    def post(self,request):
        serializer =  LoginSerializer(data=request.data)
        
        #checking if the serializer is valid 
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    