from  rest_framework.views import APIView
from core.serializers import BookSerializer, LogoutUserSerializer, PasswordResetRequestSerializer, SetNewPasswordSerializer, UserRegisterSerializer,LoginSerializer
from core.utils import send_code_to_user
from rest_framework.response import Response
from rest_framework import status
from .models import OneTimePassword,User,Book
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from  django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str,DjangoUnicodeDecodeError
from  django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser



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
    
    
    
    

class VerifyuserEmail(APIView):
    def post(self, request):
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
            # Log the exception to see what's causing the 500 error
            print(f"Error during verification: {e}")
            return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  

class  PasswordResetRequest(APIView):
  serializer_class  = PasswordResetRequestSerializer
  def post(self,request):
      serializer = self.serializer_class(data=request.data, context={'request':request})
      serializer.is_valid(raise_exception=True)
      return Response({'message':'A link has been sent to your email to reset your password.'},status=status.HTTP_200_OK) 
  
  
  
class PasswordResetConfirm(APIView):
    def post(self, request, uidb64, token):
        try:
            # Decode the uidb64 to get user ID
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            # Check if the token is valid
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'success': False, 'message': 'Token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

            # If everything is valid
            return Response({'success': True, 'message': 'Credentials are valid', 'uidb64': uidb64, 'token': token}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LogoutUserView(APIView):
    serializer_class = LogoutUserSerializer 
    permission_classes =[IsAuthenticated]

    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"Logout successfully"}, status=status.HTTP_200_OK)
    
    
class SetNewPassword(APIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save() 
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        

class Creating_BookView(APIView):
    
    permission_classes = [IsAdminUser]
    def post(self, request):
        # Creating an instance of BookSerializer
        serializer = BookSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            # Checking if a book with the same details already exists
            existing_book = Book.objects.filter(
                title=validated_data['title'],
                author=validated_data['author'],
                genre=validated_data['genre'],
                description=validated_data['description']
            ).exists()

            # If a duplicate exists, return an error
            if existing_book:
                return Response(
                    {"detail": "Book with these details already exists"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Saving the new created Book
            book = Book.objects.create(**validated_data)
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)

        # If the data is not valid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

             
# class ListingBooks(APIView):
#     def get(request,book_id=None):
#         if book_id:
#             #if book id provided, return specific book
#           book  = get_object_or_404()  


