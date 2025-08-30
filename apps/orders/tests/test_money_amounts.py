from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.restaurants.models.restaurant import Restaurant
from apps.products.models.product import Product
from apps.products.models.product_price_option import ProductPriceOption
from apps.orders.models.order import Order
from apps.restaurants.models.delivery_price import DeliveryPrice
from decimal import Decimal

class MoneyAmountsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.restaurant = Restaurant.objects.create(name="Test Restaurant", slug="test-restaurant", owner=self.user)
        
        self.product1 = Product.objects.create(name="Regular Product", price=Decimal('10.00'), restaurant=self.restaurant)
        self.product2 = Product.objects.create(name="Discounted Product", price=Decimal('20.00'), discounted_price=Decimal('15.00'), restaurant=self.restaurant)
        self.product3 = Product.objects.create(name="Multi-option Product", restaurant=self.restaurant)
        self.option1 = ProductPriceOption.objects.create(product=self.product3, name="Option 1", price=Decimal('25.00'))
        self.option2 = ProductPriceOption.objects.create(product=self.product3, name="Option 2", price=Decimal('30.00'))

        self.client.force_authenticate(user=self.user)

    def create_cart(self, items):
        url = reverse('cart-list', kwargs={'restaurant_slug': self.restaurant.slug})
        data = {
            'restaurant_slug': self.restaurant.slug,
            'items': items
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data['id']

    def get_cart(self, cart_id):
        url = reverse('cart-detail', kwargs={'restaurant_slug': self.restaurant.slug, 'pk': cart_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data

    def test_regular_price(self):
        cart_id = self.create_cart([{'product': {'id': self.product1.id}, 'quantity': 2}])
        cart_data = self.get_cart(cart_id)
        self.assertEqual(Decimal(cart_data['total_amount']), Decimal('20.00'))

    def test_discounted_price(self):
        cart_id = self.create_cart([{'product': {'id': self.product2.id}, 'quantity': 3}])
        cart_data = self.get_cart(cart_id)
        self.assertEqual(Decimal(cart_data['total_amount']), Decimal('45.00'))

    def test_multi_price_option(self):
        cart_id = self.create_cart([
            {'product': {'id': self.product3.id}, 'quantity': 2, 'selected_option_id': self.option1.id},
            {'product': {'id': self.product3.id}, 'quantity': 1, 'selected_option_id': self.option2.id}
        ])
        cart_data = self.get_cart(cart_id)
        self.assertEqual(Decimal(cart_data['total_amount']), Decimal('80.00'))

    def test_mixed_cart(self):
        cart_id = self.create_cart([
            {'product': {'id': self.product1.id}, 'quantity': 1},
            {'product': {'id': self.product2.id}, 'quantity': 2},
            {'product': {'id': self.product3.id}, 'quantity': 1, 'selected_option_id': self.option1.id},
            {'product': {'id': self.product3.id}, 'quantity': 1, 'selected_option_id': self.option2.id}
        ])
        cart_data = self.get_cart(cart_id)
        self.assertEqual(Decimal(cart_data['total_amount']), Decimal('95.00'))

    def test_cart_total_amount(self):
        cart_id = self.create_cart([
            {'product': {'id': self.product1.id}, 'quantity': 1},
            {'product': {'id': self.product2.id}, 'quantity': 2},
            {'product': {'id': self.product3.id}, 'quantity': 1, 'selected_option_id': self.option1.id},
            {'product': {'id': self.product3.id}, 'quantity': 1, 'selected_option_id': self.option2.id}
        ])
        cart_data = self.get_cart(cart_id)
        self.assertEqual(Decimal(cart_data['total_amount']), Decimal('95.00'))

    def test_order_with_mixed_cart_and_shipping(self):
        cart_id = self.create_cart([
            {'product': {'id': self.product1.id}, 'quantity': 1},
            {'product': {'id': self.product2.id}, 'quantity': 2},
            {'product': {'id': self.product3.id}, 'quantity': 1, 'selected_option_id': self.option1.id},
            {'product': {'id': self.product3.id}, 'quantity': 1, 'selected_option_id': self.option2.id}
        ])

        delivery_price = DeliveryPrice.objects.create(
            restaurant=self.restaurant,
            commune="Test Commune",
            price=Decimal('5.00')
        )

        url = reverse('order-create-from-cart', kwargs={'restaurant_slug': self.restaurant.slug})
        order_data = {
            'cart_id': cart_id,
            'payment_method': 'transferencia',
            'fulfillment_method': 'despacho',
            'full_name': 'Test Customer',
            'phone': '1234567890',
            'email': 'test@example.com',
            'address': 'Test Address',
            'delivery_price_id': delivery_price.id,
        }
        response = self.client.post(url, order_data, format='json')
        
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertIn('order', response.data)
        self.assertIn('whatsapp_message', response.data)
        
        order_data = response.data['order']
        
        self.assertIn('cart_id', order_data)
        self.assertEqual(Decimal(order_data['shipping_cost']), Decimal('5.00'))
        self.assertEqual(order_data['customer_full_name'], 'Test Customer')
        self.assertEqual(order_data['customer_address'], 'Test Address')
        self.assertEqual(order_data['customer_commune'], 'Test Commune')
        self.assertEqual(order_data['customer_phone'], '1234567890')
        self.assertEqual(order_data['fulfillment_method'], 'despacho')
        self.assertEqual(order_data['payment_method'], 'transferencia')
        
        whatsapp_message = response.data['whatsapp_message']
        self.assertIn('Test%20Customer', whatsapp_message)
        self.assertIn('despacho', whatsapp_message)
        self.assertIn('95', whatsapp_message)
        self.assertIn('5', whatsapp_message)
        self.assertIn('100', whatsapp_message)