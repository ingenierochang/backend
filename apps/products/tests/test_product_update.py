from django.test import TestCase
from PIL import Image
from io import BytesIO
from rest_framework import status
from rest_framework.test import APIClient
from apps.products.models.product import Product
from apps.restaurants.models.restaurant import Restaurant
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import json

User = get_user_model()

class TestProductUpdate(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.user, slug='test-restaurant')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.00,
            restaurant=self.restaurant
        )
        # Create a test image using PIL
        image = Image.new('RGB', (100, 100), color = 'red')
        img_io = BytesIO()
        image.save(img_io, format='JPEG')
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=img_io.getvalue(),
            content_type='image/jpeg'
        )

    def test_update_product(self):
        self.api_client.force_authenticate(user=self.user)
        url = f'/restaurants/{self.restaurant.slug}/products/{self.product.id}/'
        
        updated_data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': 15.00
        }
        
        response = self.api_client.patch(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(self.product.description, 'Updated Description')
        self.assertEqual(self.product.price, 15.00)

    def test_update_product_with_image(self):
        self.api_client.force_authenticate(user=self.user)
        url = f'/restaurants/{self.restaurant.slug}/products/{self.product.id}/'
        
        updated_data = {
            'name': 'Updated Product',
            'image': self.test_image
        }
        
        response = self.api_client.patch(url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertTrue(self.product.thumbnail_image)
        self.assertTrue(self.product.detail_image)

    def test_update_product_delete_image(self):
        self.api_client.force_authenticate(user=self.user)
        url = f'/restaurants/{self.restaurant.slug}/products/{self.product.id}/'
        
        # First, add an image to the product
        self.api_client.patch(url, {'image': self.test_image}, format='multipart')
        
        # Now, delete the image
        updated_data = {
            'thumbnail_image': '',  # Change this from None to an empty string
            'detail_image': ''      # Change this from None to an empty string
        }
        
        response = self.api_client.patch(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.product.refresh_from_db()
        self.assertFalse(self.product.thumbnail_image)
        self.assertFalse(self.product.detail_image)

    def test_update_product_unauthorized(self):
        url = f'/restaurants/{self.restaurant.slug}/products/{self.product.id}/'
        
        updated_data = {
            'name': 'Updated Product'
        }
        
        response = self.api_client.patch(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_wrong_user(self):
        wrong_user = User.objects.create_user(username='wronguser', password='wrongpass')
        self.api_client.force_authenticate(user=wrong_user)
        url = f'/restaurants/{self.restaurant.slug}/products/{self.product.id}/'
        
        updated_data = {
            'name': 'Updated Product'
        }
        
        response = self.api_client.patch(url, updated_data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # If the test fails, this will show us the actual response content
        if response.status_code != status.HTTP_403_FORBIDDEN:
            self.fail(f"Expected 403 FORBIDDEN, got {response.status_code}. Response content: {response.content}")

        # Optionally, check for a specific error message
        expected_data = {'detail': 'You do not have permission to perform this action.'}
        self.assertJSONEqual(response.content, expected_data)