import random
from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from Authentication.models import PasswordResetCode
from Authentication.serializers import (UserRegistrationSerializer,MyTokenObtainPairSerializer,
                                        ChangePasswordSerializer,ForgotPasswordEmailSerializer,
                                        PasswordResetSerializer,UserProfileSerializer,UserProfileUpdateSerializer
                                        )
# Create your views here.

User = get_user_model()

class UserRegistrationView(APIView):
    def post(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            response_data = {
                'full_name': user.full_name,
                'username': user.username,
                'email': user.email,
                'email_verification_code': user.email_verification_code
            }
            return Response({'message': 'User registered successfully', 'response_data': response_data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class EmailVerificationView(APIView):
    def post(self, request):
        verification_code = request.data.get('verification_code')
        email = request.data.get('email')

        if not verification_code or not email:
            return Response({'message': 'Verification code and email are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email_verification_code=verification_code, email=email, is_active=False)
        except User.DoesNotExist:
            return Response({'message': 'Invalid verification code or email'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = True
        user.email_verification_code = ''
        user.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Return response with tokens and user data
        return Response({
            'message': 'Email verified successfully',
            'access_token': access_token,
            'refresh_token': str(refresh),
            'user_data': {
                'full_name': user.full_name,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_200_OK)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            old_password = serializer.data.get('old_password')
            new_password = serializer.data.get('new_password')

            # Check if the new password is the same as the old one
            if user.check_password(new_password):
                return Response({'error': 'New password cannot be the same as the old one.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the old password is correct
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ForgotPasswordView(APIView):
    def generate_numeric_code(self):
        # Generate a 6-digit numeric code
        return ''.join(random.choices('0123456789', k=6))

    def post(self, request):
        serializer = ForgotPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'No user with that email address.'}, status=status.HTTP_404_NOT_FOUND)

            # Generate and store a unique 6-digit numeric code
            code = self.generate_numeric_code()
            print("Generated code:", code)  # Print the generated code for debugging purposes
            PasswordResetCode.objects.create(user=user, code=code)

            # Send the code to the user's email
            subject = 'Password Reset Code'
            message = f'Your password reset code is: {code}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            try:
                send_mail(subject, message, from_email, recipient_list, auth_user=settings.EMAIL_HOST_USER, auth_password=settings.EMAIL_HOST_PASSWORD)
                return Response({'detail': 'An email with a reset code has been sent to your email address.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': 'Failed to send the reset code. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            reset_code = serializer.validated_data['reset_code']
            new_password = serializer.validated_data['new_password']

            try:
                password_reset_code = PasswordResetCode.objects.get(code=reset_code)

                # Check if the reset code is expired
                if password_reset_code.is_expired:
                    return Response({'detail': 'The reset code has expired.'}, status=status.HTTP_400_BAD_REQUEST)

                    # Proceed with password reset
                user = password_reset_code.user
                
                # Check if the reset code is associated with a user
                user = password_reset_code.user
                if user:
                    # Check if the user's email matches the requester's email
                    if user.email != request.data.get('email'):
                        return Response({'detail': 'Invalid email for this reset code.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Invalid reset code.'}, status=status.HTTP_400_BAD_REQUEST)


                # Check if the new password is different from the old one
                if user.check_password(new_password):
                    return Response({'detail': 'New password cannot be the same as the old one.'}, status=status.HTTP_400_BAD_REQUEST)

                # Set and save the new password
                user.set_password(new_password)
                user.save()


                # Delete the reset code after successful password reset
                password_reset_code.delete()

                return Response({'detail': 'Password reset successfully.'}, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'detail': 'Invalid reset code.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer 

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(email=user.email)
        return queryset  
             
class UserProfileUpdateView(APIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)