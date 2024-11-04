from rest_framework import serializers
from .models import User, Admin, Student, Resident

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
