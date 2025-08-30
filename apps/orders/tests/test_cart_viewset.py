from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.restaurants.models.restaurant import Restaurant
from apps.products.models.product import Product
from apps.products.models.product_price_option import ProductPriceOption
from apps.orders.models.cart import Cart
from apps.orders.models.cart_item import CartItem

class CartViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.restaurant = Restaurant.objects.create(name="Test Restaurant", slug="test-restaurant", owner=self.user)
        self.product = Product.objects.create(name="Test Product", restaurant=self.restaurant)
        self.price_option = ProductPriceOption.objects.create(product=self.product, name="Regular", price=10.00)

    def test_create_cart(self):
        url = reverse('cart-list', kwargs={'restaurant_slug': self.restaurant.slug})
        data = {
            'restaurant_slug': self.restaurant.slug,
            'items': [
                {
                    'product': {'id': self.product.id},
                    'selected_option_id': self.price_option.id,
                    'quantity': 2
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('cart_id', response.data)
        self.assertEqual(Cart.objects.count(), 1)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_update_cart(self):
        cart = Cart.objects.create(restaurant=self.restaurant)
        CartItem.objects.create(cart=cart, product=self.product, product_price_option=self.price_option, quantity=1)
        
        url = reverse('cart-detail', kwargs={'restaurant_slug': self.restaurant.slug, 'pk': cart.id})
        data = {
            'items': [
                {
                    'product': {'id': self.product.id},
                    'selected_option_id': self.price_option.id,
                    'quantity': 3
                }
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.get(cart=cart).quantity, 3)

    def test_create_cart_validation_errors(self):
        url = reverse('cart-list', kwargs={'restaurant_slug': self.restaurant.slug})
        
        # Test missing restaurant_slug
        data = {'items': [{'product': {'id': self.product.id}, 'quantity': 1}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test empty items
        data = {'restaurant_slug': self.restaurant.slug, 'items': []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cart_validation_errors(self):
        cart = Cart.objects.create(restaurant=self.restaurant)
        url = reverse('cart-detail', kwargs={'restaurant_slug': self.restaurant.slug, 'pk': cart.id})
        
        # Test empty items
        data = {'items': []}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_cart(self):
        cart = Cart.objects.create(restaurant=self.restaurant)
        CartItem.objects.create(cart=cart, product=self.product, product_price_option=self.price_option, quantity=1)
        
        url = reverse('cart-detail', kwargs={'restaurant_slug': self.restaurant.slug, 'pk': cart.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 1)