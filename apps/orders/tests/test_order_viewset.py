from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.restaurants.models.restaurant import Restaurant
from apps.orders.models.order import Order
from apps.orders.models.cart import Cart
from apps.users.models import User
from decimal import Decimal
from apps.restaurants.models.delivery_price import DeliveryPrice
from apps.products.models.product import Product
from apps.orders.models.cart_item import CartItem

class OrderViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(username='owner', password='testpass')
        self.restaurant = Restaurant.objects.create(name="Test Restaurant", slug="test-restaurant", owner=self.owner)
        self.cart = Cart.objects.create(restaurant=self.restaurant)
        
        # Create a delivery price
        self.delivery_price = DeliveryPrice.objects.create(
            restaurant=self.restaurant,
            commune="Test Commune",
            price=Decimal('5.00')
        )

    def test_create_order_from_cart(self):
        # Create a cart first
        cart = Cart.objects.create(restaurant=self.restaurant)
        
        url = reverse('order-create-from-cart', kwargs={'restaurant_slug': self.restaurant.slug})
        data = {
            'cart_id': cart.id,
            'payment_method': 'transferencia',
            'fulfillment_method': 'retiro',
            'additional_instructions': 'Please make it spicy',
            'address': '123 Test St',
            'full_name': 'John Doe',
            'phone': '1234567890',
            'email': 'john@example.com'
        }
        
        # Add debugging print statements
        print("Request data:", data)
        
        response = self.client.post(url, data)
        
        # Add more debugging print statements
        print("Response status code:", response.status_code)
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.restaurant, self.restaurant)
        self.assertEqual(order.cart, cart)
        self.assertEqual(order.payment_method, 'transferencia')
        self.assertEqual(order.fulfillment_method, 'retiro')
        self.assertEqual(order.additional_instructions, 'Please make it spicy')
        self.assertEqual(order.customer_address, '123 Test St')
        self.assertEqual(order.customer_full_name, 'John Doe')
        self.assertEqual(order.customer_phone, '1234567890')
        self.assertEqual(order.customer_email, 'john@example.com')

        # New assertions to check amounts
        expected_cart_total = Decimal('0.00')  # No products in the cart
        expected_order_total = expected_cart_total  # No shipping for 'retiro'
        
        self.assertEqual(order.cart_total, expected_cart_total)
        self.assertEqual(order.order_total, expected_order_total)
        self.assertEqual(order.shipping_cost, Decimal('0.00'))
        
        # Check response data
        self.assertEqual(Decimal(response.data['order']['cart_total']), expected_cart_total)
        self.assertEqual(Decimal(response.data['order']['order_total']), expected_order_total)
        self.assertEqual(Decimal(response.data['order']['shipping_cost']), Decimal('0.00'))

    def test_list_orders_as_owner(self):
        self.client.force_authenticate(user=self.owner)
        
        # Create a Cart first
        cart = Cart.objects.create(restaurant=self.restaurant)
        
        # Now create the Order with the associated Cart
        Order.objects.create(restaurant=self.restaurant, cart=cart)
        
        url = reverse('order-list', kwargs={'restaurant_slug': self.restaurant.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_order_from_cart_with_shipping(self):
        # Create products
        product1 = Product.objects.create(name="Product 1", price=Decimal('10.00'), restaurant=self.restaurant)
        product2 = Product.objects.create(name="Product 2", price=Decimal('15.00'), restaurant=self.restaurant)
        
        # Create a cart with items
        cart = Cart.objects.create(restaurant=self.restaurant)
        CartItem.objects.create(cart=cart, product=product1, quantity=2)
        CartItem.objects.create(cart=cart, product=product2, quantity=1)
        
        url = reverse('order-create-from-cart', kwargs={'restaurant_slug': self.restaurant.slug})
        data = {
            'cart_id': cart.id,
            'payment_method': 'transferencia',
            'fulfillment_method': 'despacho',
            'additional_instructions': 'Please make it spicy',
            'address': '123 Test St',
            'full_name': 'John Doe',
            'phone': '1234567890',
            'email': 'john@example.com',
            'delivery_price_id': self.delivery_price.id
        }
        
        # Add debugging print statements
        print("Request data:", data)
        print("DeliveryPrice object:", self.delivery_price.__dict__)
        
        response = self.client.post(url, data)
        
        # Add more debugging print statements
        print("Response status code:", response.status_code)
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        
        # Verify order details
        self.assertEqual(order.restaurant, self.restaurant)
        self.assertEqual(order.cart, cart)
        self.assertEqual(order.payment_method, 'transferencia')
        self.assertEqual(order.fulfillment_method, 'despacho')
        self.assertEqual(order.additional_instructions, 'Please make it spicy')
        self.assertEqual(order.customer_address, '123 Test St')
        self.assertEqual(order.customer_commune, self.delivery_price.commune)
        self.assertEqual(order.customer_full_name, 'John Doe')
        self.assertEqual(order.customer_phone, '1234567890')
        self.assertEqual(order.customer_email, 'john@example.com')
        
        # Verify amounts
        expected_cart_total = Decimal('35.00')  # (10 * 2) + 15
        expected_shipping_cost = Decimal('5.00')
        expected_order_total = Decimal('40.00')  # 35 + 5
        
        self.assertEqual(order.cart_total, expected_cart_total)
        self.assertEqual(order.shipping_cost, expected_shipping_cost)
        self.assertEqual(order.order_total, expected_order_total)
        
        # Verify response data
        self.assertEqual(Decimal(response.data['order']['cart_total']), expected_cart_total)
        self.assertEqual(Decimal(response.data['order']['shipping_cost']), expected_shipping_cost)
        self.assertEqual(Decimal(response.data['order']['order_total']), expected_order_total)