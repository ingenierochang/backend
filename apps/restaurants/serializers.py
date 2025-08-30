from rest_framework import serializers
from apps.restaurants.models.restaurant import Restaurant
from apps.restaurants.models.banner_image import BannerImage
from apps.restaurants.models.restaurant_theme import RestaurantTheme
from apps.restaurants.models.delivery_price import DeliveryPrice

class BannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = ('id', 'image')

class DeliveryPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPrice
        fields = ['commune', 'price', 'id']

class RestaurantSerializer(serializers.ModelSerializer):
    banner_images = BannerImageSerializer(many=True, read_only=True)
    main_color = serializers.SerializerMethodField()
    delivery_prices = DeliveryPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        exclude = ['owner']

    def get_main_color(self, obj):
        # Fetch the related RestaurantTheme object
        try:
            theme = RestaurantTheme.objects.get(restaurant=obj)
            return theme.main_color
        except RestaurantTheme.DoesNotExist:
            return None