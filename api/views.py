from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
import uuid
from django.utils import timezone
from datetime import timedelta
from .models import User

# Test API (optional, you can keep it)
@api_view(['GET'])
def test_api(request):
    return Response({"status": "Backend connected successfully"})


# Register API
@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
      validate_email(email)
    except ValidationError:
      return Response(
        {'error': 'Enter a valid email address'},
        status=status.HTTP_400_BAD_REQUEST
    )
    if len(password) < 6:
        return Response(
        {'error': 'Password must be at least 6 characters long'},
        status=status.HTTP_400_BAD_REQUEST
    )

    if not re.search(r'\d', password):
        return Response(
        {'error': 'Password must contain at least one number'},
        status=status.HTTP_400_BAD_REQUEST
    )

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return Response(
            {'error': 'Password must contain at least one special character'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)


    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    return Response({'success': 'User created successfully'}, status=status.HTTP_201_CREATED)


# Login API
@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user:
        return Response({'success': 'Login successful'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


# Optional: store reset tokens in memory for demo
PASSWORD_RESET_TOKENS = {}

@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Email not registered'}, status=status.HTTP_404_NOT_FOUND)
    
    # Generate a simple reset token
    token = str(uuid.uuid4())
    
    # Store token temporarily with expiry (e.g., 15 minutes)
    PASSWORD_RESET_TOKENS[token] = {
        'user_id': user.id,
        'expires': timezone.now() + timedelta(minutes=15)
    }
    
    # For now, we return the token (in real app you would email it)
    return Response({'message': 'Password reset token generated', 'token': token}, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password(request):
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not token or not new_password:
        return Response({'error': 'Token and new password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    token_data = PASSWORD_RESET_TOKENS.get(token)
    
    if not token_data:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
    
    if token_data['expires'] < timezone.now():
        del PASSWORD_RESET_TOKENS[token]
        return Response({'error': 'Token expired'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.get(id=token_data['user_id'])
    user.set_password(new_password)
    user.save()
    
    # Delete token after successful reset
    del PASSWORD_RESET_TOKENS[token]
    
    return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
