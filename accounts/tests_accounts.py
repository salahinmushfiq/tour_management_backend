# accounts/tests_accounts.py
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


class AccountsTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        # Create users
        self.tourist = User.objects.create_user(email="tourist@example.com", password="pass1234", role="tourist")
        self.organizer = User.objects.create_user(email="organizer@example.com", password="pass1234", role="organizer")
        self.admin = User.objects.create_user(email="admin@example.com", password="pass1234", role="admin", is_staff=True)
        self.guide = User.objects.create_user(email="guide@example.com", password="pass1234", role="guide")

    # ----------------------------
    # Model Tests
    # ----------------------------
    def test_user_creation(self):
        user = User.objects.create_user(email="newuser@example.com", password="mypassword")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("mypassword"))
        self.assertEqual(user.role, "tourist")  # default

    def test_superuser_creation(self):
        superuser = User.objects.create_superuser(email="super@example.com", password="superpass")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    # ----------------------------
    # Serializer / Registration Tests
    # ----------------------------
    def test_registration_password_mismatch(self):
        url = reverse('user-register')
        data = {
            "email": "fail@example.com",
            "password": "12345678",
            "password2": "87654321"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_successful_registration(self):
        url = reverse('user-register')
        data = {
            "email": "success@example.com",
            "password": "strongpass123",
            "password2": "strongpass123"
        }
        with patch('accounts.tasks.send_welcome_email.delay') as mock_task:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            mock_task.assert_called_once()

    # ----------------------------
    # Authentication / Profile Tests
    # ----------------------------
    def test_profile_requires_authentication(self):
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_authenticated(self):
        url = reverse('user-profile')
        self.client.force_authenticate(user=self.tourist)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.tourist.email)

    # ----------------------------
    # Admin Endpoints Tests
    # ----------------------------
    def test_admin_list_permission(self):
        url = reverse('admin-user-list')
        # unauthorized user
        self.client.force_authenticate(user=self.tourist)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # admin user
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 1)

    def test_admin_update_user(self):
        url = reverse('admin-user-update', kwargs={'pk': self.tourist.id})
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, {'role': 'guide'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tourist.refresh_from_db()
        self.assertEqual(self.tourist.role, 'guide')

    # ----------------------------
    # Social Token Exchange (Mocked)
    # ----------------------------
    @patch('accounts.views.requests.get')
    def test_google_token_exchange_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"email": "social@example.com"}

        url = reverse('social_token_exchange')
        response = self.client.post(url, {"social_token": "dummy", "provider": "google"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    @patch('accounts.views.requests.get')
    def test_facebook_token_exchange_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"email": "fb@example.com"}

        url = reverse('social_token_exchange')
        response = self.client.post(url, {"social_token": "dummy", "provider": "facebook"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_social_token_exchange_invalid_provider(self):
        url = reverse('social_token_exchange')
        response = self.client.post(url, {"social_token": "token", "provider": "twitter"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------
    # Permission Tests
    # ----------------------------
    def test_role_permissions(self):
        from accounts.permissions import IsTourist, IsOrganizer, IsAdmin, IsGuide
        request = type('obj', (object,), {'user': self.tourist})()
        self.assertTrue(IsTourist().has_permission(request, None))
        self.assertFalse(IsAdmin().has_permission(request, None))
        self.assertFalse(IsGuide().has_permission(request, None))
