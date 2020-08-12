from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test public availaible ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required"""
        resource = self.client.get(INGREDIENTS_URL)

        self.assertEquals(resource.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test private availaible ingredients API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@server.com',
            'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredient list"""
        Ingredient.objects.create(user=self.user, name='Tofu')
        Ingredient.objects.create(user=self.user, name='Cale')

        resource = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(resource.status_code, status.HTTP_200_OK)
        self.assertEqual(resource.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that ingredients are limited to the user"""
        user2 = get_user_model().objects.create_user(
            'other@server.com',
            'pass123'
        )
        Ingredient.objects.create(user=user2, name='Tofu')
        ingredient = Ingredient.objects.create(user=self.user, name='Soya')

        resource = self.client.get(INGREDIENTS_URL)
        serializer = IngredientSerializer(ingredient)
        self.assertEqual(resource.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resource.data), 1)
        self.assertEqual(resource.data[0], serializer.data)
