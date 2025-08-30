from django.db import models
from apps.restaurants.models.restaurant import Restaurant
from .cart import Cart

PAYMENT_METHOD_CHOICES = (
    ('transferencia', 'Transferencia'),
)

FULFILLMENT_CHOICES = (
    ('despacho', 'Despacho'),
    ('retiro', 'Retiro'),
)

class Order(models.Model):
    TRANSFER = 'transferencia'
    DELIVERY = 'despacho'
    PICKUP = 'retiro'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    additional_instructions = models.TextField(blank=True, null=True) # the message :v
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHOD_CHOICES) # transfer only for now

    fulfillment_method = models.CharField(max_length=255, choices=FULFILLMENT_CHOICES) # delivery or pickup


    # if we ever create users for the app, this will become deprecated -> use customer_address instead
    customer_address = models.CharField(max_length=255, null=True, blank=True) 
    customer_commune = models.CharField(max_length=100, null=True, blank=True)

    # same for this shiet
    customer_full_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField(max_length=255, blank=True, null=True)

    # New fields for historical reference
    cart_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)