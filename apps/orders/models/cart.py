from django.db import models
from decimal import Decimal

class Cart(models.Model):
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_ordered = models.BooleanField(default=False)

    @property
    def total_amount(self):
        return sum((item.total_price for item in self.items.all()), Decimal('0'))