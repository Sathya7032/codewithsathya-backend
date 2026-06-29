from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from tutorials.models import UserBadge

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'xp')

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'full_name')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            full_name=validated_data.get('full_name', '')
        )
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({"new_password": "New password must be different from old password."})
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        otp_obj = user.otps.filter(otp=otp, is_verified=False).order_by('-created_at').first()
        if not otp_obj:
            raise serializers.ValidationError({"otp": "Invalid OTP code."})

        if otp_obj.is_expired():
            raise serializers.ValidationError({"otp": "OTP code has expired."})

        self.context['otp_obj'] = otp_obj
        self.context['user'] = user
        return data

    def save(self):
        user = self.context['user']
        otp_obj = self.context['otp_obj']
        new_password = self.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        otp_obj.is_verified = True
        otp_obj.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get(self.username_field)
        password = attrs.get('password')

        from django.db.models import Q
        user = User.objects.filter(Q(email=username) | Q(username=username)).first()

        if not user:
            raise AuthenticationFailed("User with this email does not exist.")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password. Please try again.")

        if not user.is_active:
            raise AuthenticationFailed("This account is inactive.")

        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'full_name': self.user.full_name,
            'xp': self.user.xp
        }
        return data


class UserBadgeSerializer(serializers.ModelSerializer):
    badge_name = serializers.CharField(source='badge.name')
    badge_description = serializers.CharField(source='badge.description')
    badge_image = serializers.ImageField(source='badge.image', read_only=True)

    class Meta:
        model = UserBadge
        fields = ('id', 'badge_name', 'badge_description', 'badge_image', 'earned_at')


class UserProfileSerializer(serializers.ModelSerializer):
    earned_badges = UserBadgeSerializer(many=True, read_only=True)
    level = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'xp', 'level', 'earned_badges')

    def get_level(self, obj):
        return (obj.xp // 1000) + 1
