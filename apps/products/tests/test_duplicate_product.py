from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth.models import User
from apps.products.models.product import Product
from apps.categories.models.category import Category
from apps.restaurants.models.restaurant import Restaurant

class ProductDuplicationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user for the owner
        self.owner = User.objects.create_user(username='testuser', password='testpassword')

        # Create a restaurant with the user as the owner
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.owner, slug='test-restaurant')

        # Create a category
        self.category = Category.objects.create(
            name='Test Category',
            order=0,
            restaurant=self.restaurant
        )

        # Create a product
        self.product = Product.objects.create(
            name='Original Product',
            description='Original description',
            price=10.00,
            category=self.category,
            restaurant=self.restaurant,
            active=True,
            order=1,
            discounted_price=8.00
        )

        # Create sample image files
        self.thumbnail_image = SimpleUploadedFile("thumbnail.jpg", b"file_content", content_type="image/jpeg")
        self.detail_image = SimpleUploadedFile("detail.jpg", b"file_content", content_type="image/jpeg")

        # Add images to the product
        self.product.thumbnail_image.save('thumbnail.jpg', self.thumbnail_image, save=True)
        self.product.detail_image.save('detail.jpg', self.detail_image, save=True)

    def test_duplicate_product(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.owner)

        url = f'/restaurants/{self.restaurant.slug}/products/{self.product.pk}/duplicate-product/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if a new product was created
        self.assertEqual(Product.objects.count(), 2)

        # Get the newly created product
        new_product = Product.objects.exclude(pk=self.product.pk).first()

        # Check if the new product has the same attributes as the original
        self.assertEqual(new_product.name, self.product.name)
        self.assertEqual(new_product.description, self.product.description)
        self.assertEqual(new_product.price, self.product.price)
        self.assertEqual(new_product.category, self.product.category)
        self.assertEqual(new_product.restaurant, self.product.restaurant)
        self.assertEqual(new_product.active, self.product.active)
        self.assertEqual(new_product.order, self.product.order)
        self.assertEqual(new_product.discounted_price, self.product.discounted_price)

        # Check if images were duplicated
        self.assertTrue(new_product.thumbnail_image)
        self.assertTrue(new_product.detail_image)
        self.assertNotEqual(new_product.thumbnail_image.name, self.product.thumbnail_image.name)
        self.assertNotEqual(new_product.detail_image.name, self.product.detail_image.name)

    def test_duplicate_product_unauthorized(self):
        # Don't authenticate the user
        url = f'/restaurants/{self.restaurant.slug}/products/{self.product.pk}/duplicate-product/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_duplicate_product_wrong_owner(self):
        # Create another user
        other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        self.client.force_authenticate(user=other_user)

        url = f'/restaurants/{self.restaurant.slug}/products/{self.product.pk}/duplicate-product/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        # Clean up created files
        self.product.thumbnail_image.delete()
        self.product.detail_image.delete()