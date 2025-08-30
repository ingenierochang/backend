from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.orders.models.order import Order
from apps.orders.models.cart import Cart
from apps.orders.models.cart_item import CartItem
from apps.products.models.product import Product
from apps.categories.models.category import Category
from apps.products.models.product_price_option import ProductPriceOption
from apps.users.models import User
from apps.orders.utils.order_message import generate_order_message
from apps.restaurants.models.restaurant import Restaurant
from apps.restaurants.models.delivery_price import DeliveryPrice

class WhatsAppMessageTestCase(TestCase):
    def setUp(self):
        # Create a user for the restaurant owner
        self.owner = User.objects.create_user(username="owner", password="ownerpass")

        # Create a restaurant
        self.restaurant = Restaurant.objects.create(name="Test Restaurant", owner=self.owner)

        # Create necessary objects for the test
        self.category1 = Category.objects.create(name="Frutos Secos y Deshidratados", restaurant=self.restaurant)
        self.category2 = Category.objects.create(name="Congelados y Frios", restaurant=self.restaurant)
        
        self.product1 = Product.objects.create(name="Jengibre Deshidratado", category=self.category1, restaurant=self.restaurant)
        self.product2 = Product.objects.create(name="Hamburguesas Seitan Vegusta 400g", category=self.category2, restaurant=self.restaurant)
        
        self.price_option1 = ProductPriceOption.objects.create(product=self.product1, name="1 KG", price=10000)
        self.price_option2 = ProductPriceOption.objects.create(product=self.product1, name="250 GR", price=2500)
        self.price_option3 = ProductPriceOption.objects.create(product=self.product2, price=4400)
        
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.cart = Cart.objects.create(restaurant=self.restaurant)
        
        CartItem.objects.create(cart=self.cart, product=self.product1, product_price_option=self.price_option1, quantity=1)
        CartItem.objects.create(cart=self.cart, product=self.product1, product_price_option=self.price_option2, quantity=1)
        CartItem.objects.create(cart=self.cart, product=self.product2, product_price_option=self.price_option3, quantity=1)
        
        self.order = Order.objects.create(
            cart=self.cart,
            restaurant=self.restaurant,
            customer_full_name="Juanito Perez",
            customer_address="NY 301, Manhattan Avenue",
            customer_commune="La Reina",
            customer_phone="+56912345678",
            fulfillment_method=Order.DELIVERY,
            payment_method=Order.TRANSFER,
            additional_instructions="Sin condimentos por favor",
            cart_total=16900,
            shipping_cost=3000,
            order_total=19900
        )

        # Create a delivery price
        self.delivery_price = DeliveryPrice.objects.create(
            restaurant=self.restaurant,
            commune="La Reina",
            price=3000
        )

    def test_generate_order_message(self):
        generated_message = generate_order_message(self.order)
        expected_message = (
            "Hola%20soy%20%2AJuanito%20Perez%2A%2C%20me%20gustar%C3%ADa%20pedir%20para%20%2Adespacho%2A%3A%0A%0A%0A"
            "%2A%C2%B7%201%20Frutos%20Secos%20y%20Deshidratados%20-%20Jengibre%20Deshidratado%20-%201%20KG%2A%0A"
            "Valor%3A%20%2A%2410%2C000%2A%0A%0A"
            "%2A%C2%B7%201%20Frutos%20Secos%20y%20Deshidratados%20-%20Jengibre%20Deshidratado%20-%20250%20GR%2A%0A"
            "Valor%3A%20%2A%242%2C500%2A%0A%0A"
            "%2A%C2%B7%201%20Congelados%20y%20Frios%20-%20Hamburguesas%20Seitan%20Vegusta%20400g%2A%0A"
            "Valor%3A%20%2A%244%2C400%2A%0A%0A%0A"
            "%2ASubtotal%3A%20%2416%2C900%2A%0A"
            "%2ADelivery%3A%20%243%2C000%2A%0A%0A"
            "%2ATotal%3A%20%2419%2C900%2A%0A%0A"
            "Mensaje%3A%20%2ASin%20condimentos%20por%20favor%2A.%0A%0A"
            "Mi%20direcci%C3%B3n%20es%20%2ANY%20301%2C%20Manhattan%20Avenue%2A%0A%0A"
            "Zona%20de%20despacho%20%2ALa%20Reina%2A%0A%0A"
            "Mi%20n%C3%BAmero%20de%20contacto%20es%20%2A%2B56912345678%2A%0A%0A"
            "Voy%20a%20pagar%20con%20%2ATransferencia%2A"
        )
        
        print("Generated message:", generated_message)
        print("Expected message:", expected_message)
        
        self.assertEqual(generated_message, expected_message)

    def test_create_order_with_whatsapp_message(self):
        client = APIClient()
        url = reverse('order-create-from-cart', kwargs={'restaurant_slug': self.restaurant.slug})
        data = {
            'cart_id': self.cart.id,
            'payment_method': 'transferencia',
            'fulfillment_method': 'despacho',
            'additional_instructions': 'Sin condimentos por favor',
            'address': 'NY 301, Manhattan Avenue',
            'full_name': 'Juanito Perez',
            'phone': '+56912345678',
            'email': 'juanito@example.com',
            'delivery_price_id': self.delivery_price.id,
            'customer_commune': 'La Reina'
        }
        
        response = client.post(url, data, format='json')
        
        print("Response status code:", response.status_code)
        print("Response data:", response.data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('whatsapp_message', response.data)
        
        whatsapp_message = response.data['whatsapp_message']
        print("WhatsApp message:", whatsapp_message)
        
        # Check if the message contains key elements instead of checking the exact start
        self.assertIn('Juanito%20Perez', whatsapp_message)
        self.assertIn('despacho', whatsapp_message)
        self.assertIn('Frutos%20Secos%20y%20Deshidratados', whatsapp_message)
        self.assertIn('Jengibre%20Deshidratado', whatsapp_message)
        self.assertIn('Congelados%20y%20Frios', whatsapp_message)
        self.assertIn('Hamburguesas%20Seitan%20Vegusta%20400g', whatsapp_message)
        self.assertIn('19%2C900', whatsapp_message)  # Total amount
        self.assertIn('Sin%20condimentos%20por%20favor', whatsapp_message)
        self.assertIn('NY%20301%2C%20Manhattan%20Avenue', whatsapp_message)
        self.assertIn('La%20Reina', whatsapp_message)
        self.assertIn('%2B56912345678', whatsapp_message)
        self.assertIn('Transferencia', whatsapp_message)