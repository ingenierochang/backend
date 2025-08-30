from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.restaurants.models.restaurant import Restaurant
from apps.restaurants.serializers import RestaurantSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.restaurants.models.banner_image import BannerImage


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from apps.restaurants.models.restaurant import Restaurant
from apps.restaurants.models.banner_image import BannerImage
from apps.restaurants.serializers import RestaurantSerializer

from apps.restaurants.models.restaurant_theme import RestaurantTheme

from apps.restaurants.models.delivery_price import DeliveryPrice
from apps.restaurants.serializers import DeliveryPriceSerializer

class RestaurantViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]

    def get_object(self, restaurant_slug):
        """
        Retrieve the restaurant by ID. For owners, check if they own the restaurant.
        """
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
        if self.request.user.is_authenticated and self.request.method != 'GET' and restaurant.owner != self.request.user:
            self.permission_denied(self.request)
        return restaurant

    def retrieve(self, request, pk=None):
        """
        Handle GET request to retrieve the details of a specific restaurant.
        """
        restaurant = self.get_object(pk)
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Handle PUT request to update the restaurant owned by the current user.
        """
        restaurant = self.get_object(pk)
        if restaurant.owner != request.user:
            return Response({"detail": "You do not have permission to edit this restaurant."}, status=status.HTTP_403_FORBIDDEN)

        serializer = RestaurantSerializer(restaurant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """
        Handle PATCH request to update the restaurant owned by the current user.
        """
        restaurant = self.get_object(pk)
        if restaurant.owner != request.user:
            return Response({"detail": "You do not have permission to edit this restaurant."}, status=status.HTTP_403_FORBIDDEN)

        serializer = RestaurantSerializer(restaurant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Handle DELETE request to delete the restaurant owned by the current user.
        """
        restaurant = self.get_object(pk)
        if restaurant.owner != request.user:
            return Response({"detail": "You do not have permission to delete this restaurant."}, status=status.HTTP_403_FORBIDDEN)

        restaurant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path="upload-banner-images")
    def upload_banner_images(self, request, pk=None):
        restaurant = self.get_object(pk)
        if not request.FILES:
            return Response({"error": "No images found in request"}, status=status.HTTP_400_BAD_REQUEST)

        for i in range(4):
            image_field = f'images_{i}'
            if image_field in request.FILES:
                image = request.FILES[image_field]
                BannerImage.objects.create(restaurant=restaurant, image=image)
        
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='delete-banner-image')
    def delete_banner_image(self, request, pk=None):
        restaurant = self.get_object(pk)
        image_id = request.data.get('image_id')

        if not image_id:
            return Response({"error": "Image ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            banner_image = BannerImage.objects.get(id=image_id, restaurant=restaurant)
            banner_image.delete()
        except BannerImage.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], url_path='update-main-color')
    def update_main_color(self, request, pk=None):
        restaurant = self.get_object(pk)
        new_color_hex = request.data.get('new_color_hex')

        if not new_color_hex:
            return Response({"error": "Color HEX is required"}, status=status.HTTP_400_BAD_REQUEST)

        restaurant_theme, created = RestaurantTheme.objects.get_or_create(restaurant=restaurant)

        try:
            restaurant_theme.main_color = new_color_hex
            restaurant_theme.save()

        except RestaurantTheme.DoesNotExist:
            return Response({"error": "RestaurantTheme not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def set_delivery_prices(self, request, pk=None):
        restaurant = self.get_object(pk)
        delivery_prices_data = request.data.get('delivery_prices', [])

        if not delivery_prices_data:
            return Response({'error': 'No delivery prices provided.'}, status=status.HTTP_400_BAD_REQUEST)

        updated_prices = []
        for price_data in delivery_prices_data:
            commune = price_data.get('commune')
            price = price_data.get('price')

            if not commune or price is None:
                return Response({'error': f'Both commune and price are required for each entry. Error in: {price_data}'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            delivery_price, created = DeliveryPrice.objects.update_or_create(
                restaurant=restaurant,
                commune=commune,
                defaults={'price': price}
            )
            updated_prices.append(delivery_price)

        serializer = DeliveryPriceSerializer(updated_prices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def delivery_prices(self, request, pk=None):
        restaurant = self.get_object(pk)
        delivery_prices = restaurant.delivery_prices.all()
        serializer = DeliveryPriceSerializer(delivery_prices, many=True)
        return Response(serializer.data)


class MyRestaurant(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        restaurants = Restaurant.objects.filter(owner=request.user).first()
        serializer = RestaurantSerializer(restaurants)
        return Response(serializer.data)