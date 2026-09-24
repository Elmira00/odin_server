from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
# from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from datetime import datetime, timedelta
from django.conf import settings
from utils.token import generate_token
from rest_framework.permissions import IsAuthenticated
from user.authentication import CustomTokenAuthentication


# @extend_schema(
#     summary="Login user",
#     description="Authenticates a user using username and password. Returns a success message and username.",
#     request=LoginSerializer,
#     responses={
#         200: OpenApiResponse(description="Login successful"),
#         400: OpenApiResponse(description="Invalid credentials or bad request")
#     },
#     tags=["Authentication"]
# )
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            remember_me = serializer.validated_data.get('remember_me', False)
            
            if remember_me:
                expire_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                expire_date = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

           
            token = generate_token(user.id, expire_date, settings.SECRET_KEY)
            
            login(request, user)  

            return Response({
                "message": "Login successful",
                "user_id": user.id,
                "expire_date": expire_date,
                "token": token
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @extend_schema(
#     summary="List all users",
#     description="Returns a list of all registered users.",
#     tags=["Users"]
# )
class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]


# @extend_schema(
#     summary="Retrieve, update, or delete a user",
#     description="Retrieve, update, or delete a specific user by ID.",
#     parameters=[OpenApiParameter(name="pk", type=int, location=OpenApiParameter.PATH, description="User ID")],
#     tags=["Users"]
# )

class UserDetail(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=[IsAuthenticated]
    authentication_classes=[CustomTokenAuthentication]

