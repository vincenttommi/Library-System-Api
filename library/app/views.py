from .serializers import PasswordResetRequestSerializer, SetNewPasswordSerializer, UserRegisterSerializer,LoginSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import send_code_to_user  
from .models import OneTimePassword, User
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404


@api_view(['POST'])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Attempt to send the code and handle any failure in sending the email
        try:
            send_code_to_user(user.email)
        except Exception as e:
            print(f"Failed to send email: {e}")
            return Response({"error": "Email sending failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Response to return when the user registration is successful
        return Response({
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
            "message": f'Hi {user.username}, thanks for signing up! A passcode has been sent to your email.'
        }, status=status.HTTP_201_CREATED)

    # Response to return if the data in the request is invalid
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    serializer  = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.data,status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def verify_user_email(request):
    otp_code = request.data.get('otp')
    if not otp_code:
        return Response({"message": "Passcode not provided"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_code_obj = OneTimePassword.objects.get(code=otp_code)
        user = user_code_obj.user
        if not user.is_verified:
            user.is_verified = True
            user.save()
            return Response({"message": "Account verified successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "User already verified"}, status=status.HTTP_200_OK)
    except OneTimePassword.DoesNotExist:
        return Response({"message": "Invalid passcode"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error during verification: {e}")
        return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def password_reset_request(request):
    serializer = PasswordResetRequestSerializer(data=request.data, context={'request':request})
    serializer.is_valid(raise_exception=True)
    return Response({"message":"A link has been sent to your email to reset password."},status=status.HTTP_200_OK)



@api_view(['POST'])
def password_reset_confirm(request,uidb64, token):
    try:
        user_id  = smart_str(urlsafe_base64_decode(uidb64))
        user  = get_object_or_404(User,id=user_id)
         
        if not PasswordResetTokenGenerator().check_token(user,token):
            return Response({'sucess':False, 'message':'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({'success':True, 'message':'Credential are valid','uidb64':uidb64,'token':token}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    


@api_view(['POST'])
def set_new_password(request):
    serializer = SetNewPasswordSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response({"message":"Password reset successful"},status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
