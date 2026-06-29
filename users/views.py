import random
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import OTPVerification
from users.serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserRegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserBadgeSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User registered successfully.",
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Generate random 6-digit OTP
        otp = f"{random.randint(100000, 999999)}"

        # Mark all previous OTPs for this user as verified/expired to prevent reuse
        OTPVerification.objects.filter(user=user, is_verified=False).update(is_verified=True)

        # Save the new OTP
        OTPVerification.objects.create(user=user, otp=otp)

        # Send OTP email
        subject = 'Password Reset OTP Code'
        message = f'Hi {user.username},\n\nYour OTP code to reset your password is {otp}. This code is valid for 10 minutes.\n\nBest regards,\nCodeWithSathya Team'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            return Response({
                "detail": f"Failed to send email: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "OTP code has been sent to your email."
        }, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Password reset successfully. You can now login with your new password."
        }, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({
            "message": "Password changed successfully."
        }, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data'].copy() if hasattr(kwargs['data'], 'copy') else dict(kwargs['data'])
            if 'username' in data and 'email' not in data:
                data['email'] = data['username']
            kwargs['data'] = data
        return super().get_serializer(*args, **kwargs)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserBadgesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        badges = request.user.earned_badges.all()
        serializer = UserBadgeSerializer(badges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
