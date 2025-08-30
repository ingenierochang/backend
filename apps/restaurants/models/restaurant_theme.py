from django.db import models
from apps.restaurants.models.restaurant import Restaurant

# Create your models here.
class RestaurantTheme(models.Model):

    # Basic
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE)

    categories_bg = models.CharField(max_length=20, blank=True, null=True) # i have no idea why i did this one, might delete

    main_color = models.CharField(max_length=20, blank=True, null=True)

    bg_color = models.CharField(max_length=20, blank=True, null=True)


    def __str__(self):

        return self.restaurant.name + " theme"
    

