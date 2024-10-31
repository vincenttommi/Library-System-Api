from rest_framework  import serializers 
from  . models  import User,Admin,Student,Resident






class UserRegisterSerializer(serializers.ModelSerializers):
    identification_photo = serializers.ImageField(write_only=True, required=False)
    school_name = serializers.CharField(write_only=True, required=False)
    school_registration_number  = serializers.CharField(write_only=True,required=False)
    address = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False)
    estate  =  serializers.CharField(write_only=True, required=False)


    class Meta:
        model = User
        fields  =  ['email','username','password','role','identification_photo','school_name','school_registration_number','address','phone_number','estate']

        extra_kwargs  = {'password':{'write_only':True}}


        def create(self, validated_data):
            role = validated_data.pop('role')
            password = validated_data.pop('password')
            user = User.objects.create_user(role=role, **validated_data)
            user.set_password(password)
            user.save()

            # Create the extended model based on the role
            if role == 'student':
                Student.objects.create(
                    user=user,
                    school_name=validated_data.get('school_name'),
                    school_registration_number=validated_data.get('school_registration_number'),
                    identification_photo=validated_data.get('identification_photo')
                )
            elif role == 'resident':
                Resident.objects.create(
                    user=user,
                    address=validated_data.get('address'),
                    phone_number=validated_data.get('phone_number'),
                    estate=validated_data.get('estate')
                )
            elif role == 'ADMIN':
                Admin.objects.create(
                    user=user,
                    identification_photo=validated_data.get('identification_photo')
                )
            return user

          




   