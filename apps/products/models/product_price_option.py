from django.db import models
from django.core.validators import MinValueValidator
from apps.products.models.product import Product
class ProductPriceOption(models.Model):
    """
        Price option for product.
        e.g. cotton shirt is $49, but german cotton shirt is $79
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True, related_name="price_options")
    name = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.product.name + " " + self.name + " price option"

    def save(self, *args, **kwargs):


        # can't have both price/discounted_price and price options
        if self.product.price or self.product.discounted_price:
            self.product.price = None
            self.product.discounted_price = None
            self.product.save()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at']