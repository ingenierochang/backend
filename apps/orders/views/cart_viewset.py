from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from apps.restaurants.models.restaurant import Restaurant
from apps.products.models.product import Product
from apps.products.models.product_price_option import ProductPriceOption
from apps.orders.models.cart import Cart
from apps.orders.models.cart_item import CartItem
from apps.orders.serializers.cart_serializer import CartSerializer
from rest_framework.exceptions import ValidationError
from apps.orders.serializers.cart_serializer import CartDetailSerializer

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def create(self, request, *args, **kwargs):
        print(f"Received data type: {type(request.data)}")
        print(f"Received data: {request.data}")

        if not isinstance(request.data, dict):
            raise ValidationError(f"Request data should be a dictionary. Received type: {type(request.data)}")

        items_data = request.data.get('items')
        restaurant_slug = request.data.get('restaurant_slug')

        if not isinstance(items_data, list):
            raise ValidationError("'items' should be a list of cart items")

        if not items_data:
            raise ValidationError("The cart cannot be empty")

        if not restaurant_slug:
            raise ValidationError("'restaurant_slug' is required")

        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)

        cart = Cart.objects.create(restaurant=restaurant)

        for item_data in items_data:
            product_data = item_data.get('product')
            if not product_data or not isinstance(product_data, dict):
                raise ValidationError(f"Valid product data is required for item: {item_data}")

            product_id = product_data.get('id')
            if not product_id:
                raise ValidationError(f"Product ID is required for item: {item_data}")

            selected_option_id = item_data.get('selected_option_id')
            quantity = item_data.get('quantity')
            if not quantity:
                raise ValidationError(f"Quantity is required for item: {item_data}")

            product = get_object_or_404(Product, id=product_id)
            price_option = None
            if product.price_options.exists():
                if not selected_option_id:
                    raise ValidationError(f"Product '{product.name}' requires a price option to be selected")
                price_option = get_object_or_404(ProductPriceOption, id=selected_option_id, product=product)
            else:
                if selected_option_id:
                    raise ValidationError(f"Product '{product.name}' does not have price options")

            CartItem.objects.create(
                cart=cart,
                product=product,
                product_price_option=price_option,
                quantity=quantity
            )

        serializer = self.get_serializer(cart)
        headers = self.get_success_headers(serializer.data)
        return Response({'cart_id': cart.id, **serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        items_data = request.data.get('items')

        if not isinstance(items_data, list):
            raise ValidationError("'items' should be a list of cart items")

        if not items_data:
            raise ValidationError("The cart cannot be empty")

        # Clear existing cart items
        instance.items.all().delete()

        for item_data in items_data:
            product = item_data.get('product')
            product_id = product.get('id')
            selected_option_id = item_data.get('selected_option_id')
            quantity = item_data.get('quantity')

            if not product_id or not quantity:
                raise ValidationError(f"Product ID and quantity are required for item: {item_data}")

            product = get_object_or_404(Product, id=product_id)
            price_option = None
            if product.price_options.exists():
                if not selected_option_id:
                    raise ValidationError(f"Product '{product.name}' requires a price option to be selected")
                price_option = get_object_or_404(ProductPriceOption, id=selected_option_id, product=product)
            else:
                if selected_option_id:
                    raise ValidationError(f"Product '{product.name}' does not have price options")

            CartItem.objects.create(
                cart=instance,
                product=product,
                product_price_option=price_option,
                quantity=quantity
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # i think im not even using this shit
    # @action(detail=False, methods=['GET'])
    # def get_or_create(self, request):
    #     cart_id = request.query_params.get('cart_id')
    #     if cart_id:
    #         cart = get_object_or_404(Cart, id=cart_id)
    #     else:
    #         restaurant_slug = request.query_params.get('restaurant_slug')
    #         if not restaurant_slug:
    #             raise ValidationError("restaurant_slug is required when creating a new cart")
    #         restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
    #         cart = Cart.objects.create(restaurant=restaurant)
    #     serializer = self.get_serializer(cart)
    #     return Response({'cart_id': cart.id, **serializer.data})

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CartDetailSerializer
        return CartSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)