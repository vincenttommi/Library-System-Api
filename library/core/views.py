from datetime import datetime, timedelta
from  rest_framework.views import APIView
from core.serializers import BookSerializer, LogoutUserSerializer, PasswordResetRequestSerializer, SetNewPasswordSerializer, UserRegisterSerializer,LoginSerializer
from core.utils import send_code_to_user
from rest_framework.response import Response
from rest_framework import status
from .models import Borrowing, OneTimePassword,User,Book
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from  django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str,DjangoUnicodeDecodeError
from  django.contrib.auth.tokens import PasswordResetTokenGenerator
from .permissions import IsAdmin
from django.shortcuts import get_object_or_404
from  rest_framework.permissions import IsAuthenticated
from rest_framework import permissions, status
import logging





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
    
    permission_classes = [IsAdmin]

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

class ListingBooks(APIView):
    def get(self, request, id=None):  # Accept 'id' as a path parameter
        if id:  # Use the path parameter to fetch the book
            try:
                book = Book.objects.get(pk=id)
                serializer = BookSerializer(book)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Book.DoesNotExist:
                return Response(
                    {"detail": "Book not found"}, status=status.HTTP_404_NOT_FOUND
                )
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Invalid book ID format"}, status=status.HTTP_400_BAD_REQUEST
                )

        # If no ID is provided, return the full list
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
 
 
class EditBook(APIView):

    permission_classes = [IsAdmin]

    def put(self, request, id):
        """
        Edit a book with the given id
        """
        book = get_object_or_404(Book, pk=id)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": 201, "message": "Book edited successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"status": 400, "message": "Validation error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

            
        
class DeleteBook(APIView):
    
    permission_classes = [IsAdmin]
    
    def delete(self,request, book_id):
        try:
            book = Book.objects.get(pk=book_id)
            book.delete()
            return Response({"message": "Book deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    



class BorrowBook(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        book_id = request.data.get("bookId")
        if not book_id:
            return Response(
                {"status": 400, "message": "bookId is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate book existence
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(
                {"status": 400, "message": "Book not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Log the author field to see what's being returned
        print(f"Book author: {book.author}")

        # Ensure the book has an associated author (it should be an Author object)
        if not book.author:
            return Response(
                {"status": 400, "message": "Book has no associated author."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Borrowing logic
        date_borrowed = datetime.now().date()
        due_date = date_borrowed + timedelta(days=7)

        borrowing = Borrowing.objects.create(
            user=request.user,  # Using authenticated user
            book=book,
            date_borrowed=date_borrowed,
            due_date=due_date,
        )

        # Response data
        response_data = {
    "status": 201,
    "message": "Book borrowed successfully",
    "data": {
        "book": {
            "title": book.title,
            "author": {
                "name": book.author,  # Use the CharField value
            },
            "genre": book.genre,
            "description": book.description,
            "availability": book.availability,
            "createdAt": book.created_at,
        },
        "dateBorrowed": borrowing.date_borrowed,
        "dueDate": borrowing.due_date,
        "borrowedBy": {
            "id": request.user.id,
            "name": getattr(request.user, "name", "Unknown"),
        },
    },
}

        return Response(response_data, status=status.HTTP_201_CREATED)



class ReturnBook(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        book_id = request.data.get("bookId")
        if not book_id:
            return Response(
                {"status": 400, "message": "bookId is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if book exists
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(
                {"status": 400, "message": "Book not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Retrieve all borrowing records for the user and book
        borrowings = Borrowing.objects.filter(
            book=book, user=request.user, due_date__gte=datetime.now().date()
        )

        if not borrowings.exists():
            return Response(
                {"status": 400, "message": "You have not borrowed this book or it is already returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete all borrowing records for this book by the user
        borrowings.delete()

        # Mark the book as available
        book.availability = True
        book.save()

        # Response
        response_data = {
            "status": 201,
            "message": "Book returned successfully",
            "data": {
                "title": book.title,
                "author": {
                    "name": book.author,
                },
                "genre": book.genre,
                "description": book.description,
                "availability": book.availability,
            },
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
         