from django.db import models
from django.core.validators import MinValueValidator
from .restaurant import Restaurant

class DeliveryPrice(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='delivery_prices', on_delete=models.CASCADE)
    commune = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('restaurant', 'commune')

    def __str__(self):
        return f"{self.restaurant.name} - {self.commune}: ${self.price}"