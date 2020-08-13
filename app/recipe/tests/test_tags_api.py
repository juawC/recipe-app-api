from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def sample_recipe(user, **params):
    """Creates and returns a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicTagsApiTest(TestCase):
    """Test the public availaible tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@server.com',
            'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        resource = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(resource.status_code, status.HTTP_200_OK)
        self.assertEqual(resource.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags are limited to the user"""
        user2 = get_user_model().objects.create_user(
            'other@server.com',
            'pass123'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        resource = self.client.get(TAGS_URL)
        serializer = TagSerializer(tag)
        self.assertEqual(resource.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resource.data), 1)
        self.assertEqual(resource.data[0], serializer.data)

    def test_create_tag_successfully(self):
        """Test creates new tag successfully"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid_payload(self):
        """Test creating new tag with invalid payload"""
        payload = {'name': ''}
        resource = self.client.post(TAGS_URL, payload)

        self.assertEquals(resource.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(tag1)

        resource = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, resource.data)
        self.assertNotIn(serializer2.data, resource.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = sample_recipe(user=self.user, title='Pancakes')
        recipe1.tags.add(tag)
        recipe2 = sample_recipe(user=self.user, title='Porridge')
        recipe2.tags.add(tag)

        resource = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(resource.data), 1)
