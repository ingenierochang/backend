from rest_framework import serializers
from apps.orders.models.order import Order
from apps.restaurants.serializers import RestaurantSerializer
from apps.orders.models.cart import Cart
from apps.restaurants.models.restaurant import Restaurant

class OrderSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), write_only=True)
    cart_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'restaurant', 'cart', 'cart_total', 'shipping_cost', 'order_total',
                  'payment_method', 'fulfillment_method', 'additional_instructions', 
                  'customer_address', 'customer_commune', 'customer_full_name',
                  'customer_phone', 'customer_email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'cart_total', 'shipping_cost', 'order_total', 'created_at', 'updated_at']

    def create(self, validated_data):
        cart = validated_data.pop('cart')
        order = Order.objects.create(
            restaurant=cart.restaurant,
            cart=cart,
            **validated_data
        )
        return order

class OrderCreateSerializer(serializers.ModelSerializer):
    cart_id = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), source='cart')
    restaurant_slug = serializers.SlugRelatedField(
        queryset=Restaurant.objects.all(),
        slug_field='slug',
        source='restaurant'
    )

    class Meta:
        model = Order
        fields = ['cart_id', 'restaurant_slug', 'customer_full_name', 'customer_address', 'customer_commune', 'customer_phone', 'fulfillment_method', 'payment_method', 'additional_instructions', 'shipping_cost']

    def create(self, validated_data):
        cart = validated_data.pop('cart')
        restaurant = validated_data.pop('restaurant')
        shipping_cost = validated_data.pop('shipping_cost', 0)

        # Calculate cart_total
        cart_total = sum(item.total_price for item in cart.items.all())

        # Calculate order_total
        order_total = cart_total + shipping_cost

        order = Order.objects.create(
            cart=cart,
            restaurant=restaurant,
            cart_total=cart_total,
            shipping_cost=shipping_cost,
            order_total=order_total,
            **validated_data
        )
        return order