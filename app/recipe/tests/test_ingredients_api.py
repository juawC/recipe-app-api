from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def sample_recipe(user, **params):
    """Creates and returns a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


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

    def test_create_ingredient_successfully(self):
        """Test creates new ingredient successfully"""
        payload = {'name': 'Paperika'}
        self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid_payload(self):
        """Test creating new ingredient with invalid payload"""
        payload = {'name': ''}
        resource = self.client.post(INGREDIENTS_URL, payload)

        self.assertEquals(resource.status_code, status.HTTP_400_BAD_REQUEST)

        def test_retrieve_ingredients_assigned_to_recipes(self):
            """Test filtering ingredients by those assigned to recipes"""
            ingredient1 = Ingredient.objects.create(
                user=self.user, name='Apples'
            )
            ingredient2 = Ingredient.objects.create(
                user=self.user, name='Turkey'
            )
            recipe = sample_recipe(
                user=self.user,
                title='Apple crumble'
            )
            recipe.ingredients.add(ingredient1)

            resource = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

            serializer1 = IngredientSerializer(ingredient1)
            serializer2 = IngredientSerializer(ingredient2)
            self.assertIn(serializer1.data, resource.data)
            self.assertNotIn(serializer2.data, resource.data)

    def test_retrieve_ingredient_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe1 = sample_recipe(
            user=self.user,
            title='Eggs benedict'
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = sample_recipe(
            user=self.user,
            title='Green eggs on toast'
        )
        recipe2.ingredients.add(ingredient)

        resource = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(resource.data), 1)
