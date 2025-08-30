from django.contrib import admin
from apps.restaurants.models.restaurant import Restaurant
from apps.restaurants.models.restaurant_theme import RestaurantTheme
from apps.restaurants.models.banner_image import BannerImage
from apps.restaurants.models.delivery_price import DeliveryPrice

# Register your models here.

admin.site.register(Restaurant)
admin.site.register(RestaurantTheme)
admin.site.register(BannerImage)
admin.site.register(DeliveryPrice)