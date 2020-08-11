from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_email_successfull(self):
        """Test creating a new user with an email is successfull"""
        email = 'email@server.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEquals(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_is_normalized(self):
        """Test creating a new user the email gets normalized"""
        email = 'email@SERVER.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEquals(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a new user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_super_user(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(
            email='email@server.com',
            password='pass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
