from django.contrib import admin
from apps.products.models.product import Product
from apps.products.models.product_price_option import ProductPriceOption

# Register your models here.

admin.site.register(Product)
admin.site.register(ProductPriceOption)
# admin.site.register(Category)