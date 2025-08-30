import io
import pandas as pd
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models.product import Product
from apps.categories.models.category import Category
from apps.restaurants.models.restaurant import Restaurant

class BulkUploadProductsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(username='testuser', password='testpassword')
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.owner)
        self.client.force_authenticate(user=self.owner)

    def create_excel_file(self, data):
        df = pd.DataFrame(data)
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        return excel_file

    def test_bulk_upload_success(self):
        data = [
            {'name': 'Product 1', 'category': 'Category 1', 'description': 'Desc 1', 'price': 10.5, 'active': True, 'order': 1},
            {'name': 'Product 2', 'category': 'Category 2', 'description': 'Desc 2', 'price': 15.0, 'active': False, 'order': 2},
        ]
        excel_file = self.create_excel_file(data)
        
        url = f'/restaurants/{self.restaurant.slug}/products/bulk-upload/'
        response = self.client.post(url, {'file': excel_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Category.objects.count(), 2)

    def test_bulk_upload_missing_required_columns(self):
        data = [
            {'name': 'Product 1'},  # Missing 'category'
        ]
        excel_file = self.create_excel_file(data)
        
        url = f'/restaurants/{self.restaurant.slug}/products/bulk-upload/'
        response = self.client.post(url, {'file': excel_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Excel file is missing required columns", response.json()['error'])

    def test_bulk_upload_invalid_data(self):
        data = [
            {'name': 'Product 1', 'category': 'Category 1', 'price': 'invalid'},
        ]
        excel_file = self.create_excel_file(data)
        
        url = f'/restaurants/{self.restaurant.slug}/products/bulk-upload/'
        response = self.client.post(url, {'file': excel_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # It should still create the product, just without the invalid price
        self.assertEqual(Product.objects.count(), 1)
        self.assertIsNone(Product.objects.first().price)

    def test_bulk_upload_no_file(self):
        url = f'/restaurants/{self.restaurant.slug}/products/bulk-upload/'
        response = self.client.post(url, {}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], "No file uploaded")

    def test_bulk_upload_unauthorized(self):
        self.client.force_authenticate(user=None)
        data = [
            {'name': 'Product 1', 'category': 'Category 1'},
        ]
        excel_file = self.create_excel_file(data)
        
        url = f'/restaurants/{self.restaurant.slug}/products/bulk-upload/'
        response = self.client.post(url, {'file': excel_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
