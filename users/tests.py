import datetime
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import OTPVerification

User = get_user_model()

class AuthAPITests(APITestCase):

    def setUp(self):
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.token_refresh_url = reverse('users:token_refresh')
        self.forgot_password_url = reverse('users:forgot_password')
        self.reset_password_url = reverse('users:reset_password')
        self.change_password_url = reverse('users:change_password')

        # Create a test user
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'full_name': 'Test User'
        }
        self.user = User.objects.create_user(
            username=self.user_data['email'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            full_name=self.user_data['full_name']
        )

    def test_user_registration_success(self):
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'full_name': 'New User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        # Check that the username is set to email value
        self.assertEqual(response.data['user']['username'], 'newuser@example.com')
        self.assertEqual(response.data['user']['full_name'], 'New User')
        self.assertTrue(User.objects.filter(email='newuser@example.com', full_name='New User').exists())

    def test_user_registration_duplicate_email(self):
        data = {
            'email': self.user_data['email'],  # Duplicate
            'password': 'newpassword123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_success(self):
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Verify user details are included in the login response
        self.assertIn('user', response.data)
        user_info = response.data['user']
        self.assertEqual(user_info['id'], self.user.id)
        self.assertEqual(user_info['email'], self.user_data['email'])
        self.assertEqual(user_info['first_name'], self.user_data['first_name'])
        self.assertEqual(user_info['last_name'], self.user_data['last_name'])
        self.assertEqual(user_info['full_name'], 'Test User')

    def test_login_success_with_username_key(self):
        data = {
            'username': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])

    def test_login_failure(self):
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        # 1. Login to get token
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']

        # 2. Authenticate
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 3. Call Logout with refresh token
        logout_data = {'refresh': refresh_token}
        response = self.client.post(self.logout_url, logout_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful.')

    def test_logout_unauthorized(self):
        # Call Logout without active access token credentials
        response = self.client.post(self.logout_url, {'refresh': 'somerefreshtoken'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        # First login to get a refresh token
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh']

        # Call refresh token endpoint
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.token_refresh_url, refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_forgot_password_success(self):
        data = {'email': self.user_data['email']}
        response = self.client.post(self.forgot_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that OTPVerification object is created
        self.assertEqual(OTPVerification.objects.filter(user=self.user).count(), 1)
        # Check that the email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset OTP Code', mail.outbox[0].subject)
        # Verify the OTP is in the email body
        otp = OTPVerification.objects.get(user=self.user).otp
        self.assertIn(otp, mail.outbox[0].body)

    def test_forgot_password_nonexistent_email(self):
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.forgot_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_success(self):
        # Trigger forgot password to generate OTP
        self.client.post(self.forgot_password_url, {'email': self.user_data['email']})
        otp_verification = OTPVerification.objects.get(user=self.user)
        otp = otp_verification.otp

        # Reset password
        reset_data = {
            'email': self.user_data['email'],
            'otp': otp,
            'new_password': 'newsecretpassword'
        }
        response = self.client.post(self.reset_password_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check password is reset
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newsecretpassword'))
        # Check OTP is marked verified
        otp_verification.refresh_from_db()
        self.assertTrue(otp_verification.is_verified)

    def test_reset_password_expired_otp(self):
        # Trigger forgot password to generate OTP
        self.client.post(self.forgot_password_url, {'email': self.user_data['email']})
        otp_verification = OTPVerification.objects.get(user=self.user)
        
        # Manually force OTP expiration back in time
        otp_verification.created_at = timezone.now() - datetime.timedelta(minutes=15)
        otp_verification.save()

        reset_data = {
            'email': self.user_data['email'],
            'otp': otp_verification.otp,
            'new_password': 'newsecretpassword'
        }
        response = self.client.post(self.reset_password_url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('otp', response.data)

    def test_change_password_success(self):
        # Login to get access token
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data['access']

        # Set Authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        change_data = {
            'old_password': self.user_data['password'],
            'new_password': 'updatedpassword123'
        }
        response = self.client.post(self.change_password_url, change_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify password is updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('updatedpassword123'))

    def test_change_password_wrong_old_password(self):
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        change_data = {
            'old_password': 'wrongpassword123',
            'new_password': 'updatedpassword123'
        }
        response = self.client.post(self.change_password_url, change_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Old password is not correct.')

    def test_registration_error_contains_detail(self):
        data = {
            'email': self.user_data['email'],  # Duplicate
            'password': 'newpassword123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'A user with this email already exists.')

