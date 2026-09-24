from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings
from utils.token import generate_token

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user_id = request.headers.get('X-User-Id')
        expire_date = request.headers.get('X-Expire-Date')
        token = request.headers.get('X-Auth-Token')

        if not all([user_id, expire_date, token]):
            return None  
        
       
        try:
            expire_dt = datetime.strptime(expire_date, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise AuthenticationFailed("Invalid expire_date format")
        
        if datetime.utcnow() > expire_dt:
            raise AuthenticationFailed("Token expired")

        
        expected_token = generate_token(int(user_id), expire_date, settings.SECRET_KEY)
        if token != expected_token:
            raise AuthenticationFailed("Invalid token")

        
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, None)
