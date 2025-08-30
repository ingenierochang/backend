from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.products.models.product import Product
from apps.categories.models.category import Category
from apps.restaurants.models.restaurant import Restaurant

class ProductsCategoriesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user for the owner
        self.owner = User.objects.create_user(username='testuser', password='testpassword')

        # Create a restaurant with the user as the owner
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.owner)

        # Create categories
        self.category1 = Category.objects.create(
            name='Almuerzos',
            order=0,
            restaurant=self.restaurant
        )
        self.category2 = Category.objects.create(
            name='Postres',
            order=1,
            restaurant=self.restaurant
        )

        # Create products
        Product.objects.create(
            name='Product 1',
            category=self.category1,
            restaurant=self.restaurant,
            order=0
        )
        Product.objects.create(
            name='Product 2',
            category=self.category1,
            restaurant=self.restaurant,
            order=1
        )
        Product.objects.create(
            name='Product 3',
            category=self.category2,
            restaurant=self.restaurant,
            order=0
        )
        Product.objects.create(
            name='Product 4',
            category=self.category2,
            restaurant=self.restaurant,
            order=1
        )

    def test_products_categories(self):
        url = f'/restaurants/{self.restaurant.slug}/products/products-categories/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertIn('Almuerzos', response_data)
        self.assertIn('Postres', response_data)

        almuerzos_products = response_data['Almuerzos']
        self.assertEqual(len(almuerzos_products), 2)
        self.assertEqual(almuerzos_products[0]['name'], 'Product 1')
        self.assertEqual(almuerzos_products[1]['name'], 'Product 2')

        postres_products = response_data['Postres']
        self.assertEqual(len(postres_products), 2)
        self.assertEqual(postres_products[0]['name'], 'Product 3')
        self.assertEqual(postres_products[1]['name'], 'Product 4')
