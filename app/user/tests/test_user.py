from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successfull"""
        payload = {
            'email': 'email@server.com',
            'password': 'pass123',
            'name': 'Test name',
        }
        resource = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(resource.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**resource.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', resource.data)

    def test_user_exists(self):
        """Test that creating an already existing user fails"""
        payload = {
            'email': 'email@server.com',
            'password': 'pass123',
            'name': 'Test name',
        }
        create_user(**payload)
        resource = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(resource.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'email@server.com',
            'password': 'pw',
            'name': 'Test name',
        }
        resource = self.client.post(CREATE_USER_URL, payload)

        self.assertEquals(resource.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that token is created for the user"""
        payload = {'email': 'email@server.com', 'password': 'pass123'}
        create_user(**payload)
        resource = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', resource.data)
        self.assertEquals(resource.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if the credentials are invalid"""
        payload = {'email': 'email@server.com', 'password': 'pass123'}
        create_user(**payload)
        payload['password'] = 'wrong'
        resource = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', resource.data)
        self.assertEquals(resource.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if the user does not exist"""
        payload = {'email': 'email@server.com', 'password': 'pass123'}
        resource = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', resource.data)
        self.assertEquals(resource.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that token is not created if the the password field is blank"""
        payload = {'email': 'email@server.com', 'password': ''}
        resource = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', resource.data)
        self.assertEquals(resource.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        resource = self.client.post(ME_URL)

        self.assertEquals(resource.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests API require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@server',
            password='pass123',
            name='test',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retrieving profile for login user"""
        resource = self.client.get(ME_URL)

        self.assertEquals(resource.status_code, status.HTTP_200_OK)
        self.assertEquals(
            resource.data,
            {'name': self.user.name, 'email': self.user.email}
        )

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpass123'}

        resource = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(resource.status_code, status.HTTP_200_OK)
