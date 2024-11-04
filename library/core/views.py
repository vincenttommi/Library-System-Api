from .serializers import UserRegisterSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utilis import send_code_to_user  
from .models import OneTimePassword
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError

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
