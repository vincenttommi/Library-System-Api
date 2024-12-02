from rest_framework  import serializers
from  .models import  User
from rest_framework.exceptions import AuthenticationFailed




class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=20, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=20, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password2', 'name', 'account_type', 'country',
            'country_code', 'state', 'address', 'phone_number'
        ]

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            account_type=validated_data['account_type'],
            country=validated_data['country'],
            country_code=validated_data['country_code'],
            state=validated_data['state'],
            address=validated_data['address'],
            phone_number=validated_data['phone_number']
        )

        return user




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        fields = ['email', 'password', 'name', 'access_token', 'refresh_token']

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
        attrs['name'] = user.name  
        attrs['access_token'] = str(user_token.get('access'))
        attrs['refresh_token'] = str(user_token.get('refresh'))
        attrs['user'] = user 

        return attrs