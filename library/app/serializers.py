from rest_framework import serializers
from .models import User, Admin, Student, Resident
from .utilis import send_code_to_user
from django.utils.encoding import smart_str, smart_bytes, force_str
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode 






class UserRegisterSerializer(serializers.ModelSerializer):
    identification_photo = serializers.ImageField(write_only=True, required=False)
    school_name = serializers.CharField(write_only=True, required=False)
    school_registration_number = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False)
    estate = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'role',
            'identification_photo', 'school_name', 
            'school_registration_number', 'address', 
            'phone_number', 'estate'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Extract role and password
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        
        # Separate User data from role-specific data
        user_data = {
            "email": validated_data.get('email'),
            "username": validated_data.get('username'),
        }

        # Create the User instance
        user = User.objects.create_user(role=role, **user_data)
        user.set_password(password)
        user.save()

        # Role-specific data handling
        if role == 'student':
            Student.objects.create(
                user=user,
                school_name=validated_data.pop('school_name', None),
                school_registration_number=validated_data.pop('school_registration_number', None),
                identification_photo=validated_data.pop('identification_photo', None)
            )
        elif role == 'resident':
            Resident.objects.create(
                user=user,
                address=validated_data.pop('address', None),
                phone_number=validated_data.pop('phone_number', None),
                estate=validated_data.pop('estate', None)
            )
        elif role == 'admin':
            Admin.objects.create(
                user=user,
                identification_photo=validated_data.pop('identification_photo', None)
            )
        
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    role = serializers.CharField(max_length=68, read_only=True)
    username = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        fields = ['email', 'password', 'username', 'role', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # User retrieval
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid credentials, try again')

        # Password check
        if not user.check_password(password):
            raise AuthenticationFailed('Invalid credentials, try again')

        # Check if user is verified
        if not user.is_verified:
            raise AuthenticationFailed('Your email is not verified. Please verify your email before logging in.')

        # Token generation
        user_token = user.tokens()  # Ensure this is returning a dictionary, not a string

        # Add user details to validated attrs
        attrs['username'] = user.username
        attrs['role'] = user.role
        attrs['access_token'] = str(user_token.get('access'))
        attrs['refresh_token'] = str(user_token.get('refresh'))
        attrs['user'] = user 

        return attrs
    



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():  # Use exists() for checking
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            # Accessing the request context properly
            request = self.context.get('request')
            site_domain = get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            abslink = f"http://{site_domain}{relative_link}"
            email_body = f"Hi, use the link below to reset your password:\n{abslink}"

            data = {
                'email_body': email_body,
                'email_subject': "Reset your password",
                'to_email': user.email
            }
            send_code_to_user(data)
        else:
            raise serializers.ValidationError("User with this email does not exist.")
        
        return attrs


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        # Check if the passwords match
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        # Decode the uidb64
        user_id = force_str(urlsafe_base64_decode(uidb64))
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found.")

        # Validate the token
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise AuthenticationFailed('Reset link is invalid or expired.')

        # If everything is fine, return the user object
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        user.set_password(validated_data['password'])
        user.save()
        return user