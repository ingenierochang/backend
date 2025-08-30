from rest_framework import serializers
from apps.orders.models.cart import Cart
from apps.orders.models.cart_item import CartItem
from apps.restaurants.serializers import RestaurantSerializer
from apps.products.models.product import Product
from apps.products.models.product_price_option import ProductPriceOption
from django.shortcuts import get_object_or_404
from apps.restaurants.models.restaurant import Restaurant
from apps.products.serializers.product_serializer import ProductSerializer
from apps.products.serializers.product_price_option_serializer import ProductPriceOptionSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_price_option = serializers.PrimaryKeyRelatedField(queryset=ProductPriceOption.objects.all(), required=False)
    quantity = serializers.IntegerField(min_value=1)
    selected_option_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = CartItem
        fields = ['product', 'product_price_option', 'quantity', 'selected_option_id']

    def to_internal_value(self, data):
        if isinstance(data.get('product'), dict):
            data['product'] = data['product'].get('id')
        if 'selected_option_id' in data:
            data['product_price_option'] = data.pop('selected_option_id')
        return super().to_internal_value(data)

class CartItemDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    product_price_option = ProductPriceOptionSerializer()
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = ['product', 'product_price_option', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, required=False)
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_slug = serializers.CharField(write_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'restaurant', 'is_ordered', 'items', 'created_at', 'updated_at', 'restaurant_slug']
        read_only_fields = ['id', 'is_ordered', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        restaurant_slug = validated_data.pop('restaurant_slug')
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)

        # Remove 'restaurant' from validated_data if it exists
        validated_data.pop('restaurant', None)

        cart = Cart.objects.create(restaurant=restaurant, **validated_data)

        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)

        return cart

class CartDetailSerializer(serializers.ModelSerializer):
    items = CartItemDetailSerializer(many=True, read_only=True)
    restaurant = RestaurantSerializer()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'restaurant', 'is_ordered', 'items', 'created_at', 'updated_at', 'total_amount']