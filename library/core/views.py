from .serializers  import UserRegisterSerializer
from  rest_framework import status
from  rest_framework.decorators import api_view
from  rest_framework.response  import  Response



@api_view(['POST'])
def register_user(request):
    serializer  = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "user":{
                "id":user.id,
                "email":user.email,
                "username":user.username,
                "role":user.role ,
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status.status.HTTP_400_BAD_REQUEST)
    


