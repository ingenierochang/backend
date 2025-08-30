from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.restaurants.models.restaurant import Restaurant
from apps.restaurants.models.delivery_price import DeliveryPrice

class DeliveryPricesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.restaurant = Restaurant.objects.create(name='Test Restaurant', owner=self.user, slug='test-restaurant')
        self.client.force_authenticate(user=self.user)

    def test_set_delivery_prices(self):
        url = reverse('restaurant-set-delivery-prices', kwargs={'pk': self.restaurant.slug})
        data = {
            'delivery_prices': [
                {'commune': 'Commune1', 'price': 1000},
                {'commune': 'Commune2', 'price': 1500},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(DeliveryPrice.objects.count(), 2)

    def test_set_delivery_prices_invalid_data(self):
        url = reverse('restaurant-set-delivery-prices', kwargs={'pk': self.restaurant.slug})
        data = {
            'delivery_prices': [
                {'commune': 'Commune1', 'price': 1000},
                {'commune': 'Commune2'},  # Missing price
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_set_delivery_prices_no_data(self):
        url = reverse('restaurant-set-delivery-prices', kwargs={'pk': self.restaurant.slug})
        data = {'delivery_prices': []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_get_delivery_prices(self):
        DeliveryPrice.objects.create(restaurant=self.restaurant, commune='Commune1', price=1000)
        DeliveryPrice.objects.create(restaurant=self.restaurant, commune='Commune2', price=1500)

        url = reverse('restaurant-delivery-prices', kwargs={'pk': self.restaurant.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_delivery_prices_empty(self):
        url = reverse('restaurant-delivery-prices', kwargs={'pk': self.restaurant.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_set_delivery_prices_unauthorized(self):
        self.client.logout()
        url = reverse('restaurant-set-delivery-prices', kwargs={'pk': self.restaurant.slug})
        data = {
            'delivery_prices': [
                {'commune': 'Commune1', 'price': 1000},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

