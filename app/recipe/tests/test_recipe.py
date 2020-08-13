from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Creates and returns a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Tests unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required"""
        resource = self.client.get(RECIPE_URL)

        self.assertEquals(resource.status_code, status.HTTP_401_UNAUTHORIZED)


class PriceRecipeApiTests(TestCase):
    """Tests authenticated recipe API access"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@server.com',
            'pass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving recipes"""
        sample_recipe(user=self.user, title='recipe1')
        sample_recipe(user=self.user, title='recipe2')

        resource = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(resource.status_code, status.HTTP_200_OK)
        self.assertEqual(resource.data, serializer.data)

    def test_retrieve_recipes_limited_to_user(self):
        """Test retrieving recipes limited to user"""
        other_user = get_user_model().objects.create_user(
            'other_test@server.com',
            'pass123'
        )

        sample_recipe(user=self.user, title='recipe1')
        sample_recipe(user=other_user, title='recipe2')

        resource = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(len(resource.data), 1)
        self.assertEqual(resource.data, serializer.data)
