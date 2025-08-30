from django.contrib import admin

from apps.orders.models.cart_item import CartItem
from apps.orders.models.order import Order
from apps.orders.models.cart import Cart

# Register your models here.

admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Cart)