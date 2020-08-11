from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@server.com',
            password='pass123'
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='user@server.com',
            password='pass123',
            name='Test user'
        )

    def test_user_listed(self):
        """Test that users are listed on the user page"""
        url = reverse('admin:core_user_changelist')
        resource = self.client.get(url)

        self.assertContains(resource, self.user.name)
        self.assertContains(resource, self.user.email)

    def test_user_change_page(self):
        """Test that user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        resource = self.client.get(url)

        self.assertEquals(resource.status_code, 200)

    def test_create_user_page(self):
        """Test create user page works"""
        url = reverse('admin:core_user_add')
        resource = self.client.get(url)

        self.assertEquals(resource.status_code, 200)
