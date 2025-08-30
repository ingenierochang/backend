from django.db import models
from django.core.exceptions import ValidationError
from apps.products.models.product import Product
from apps.orders.models.cart import Cart
from decimal import Decimal

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_price_option = models.ForeignKey('products.ProductPriceOption', null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        try:
            if self.product_price_option:
                price = self.product_price_option.price
            else:
                price = min(
                    filter(None, [self.product.price, self.product.discounted_price]),
                    default=Decimal('0')
                )
            return max(Decimal('0'), price) * self.quantity
        except Product.DoesNotExist:
            return Decimal('0')

    def clean(self):
        super().clean()
        if self.product_price_option and self.product_price_option.product != self.product:
            raise ValidationError("The price option does not belong to the selected product.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)