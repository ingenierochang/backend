from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.orders.models.order import Order
from apps.orders.serializers.order_serializer import OrderCreateSerializer
from apps.orders.models.cart import Cart
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.restaurants.models.restaurant import Restaurant
from decimal import Decimal
from apps.restaurants.models.delivery_price import DeliveryPrice
from apps.orders.utils.order_message import generate_order_message
from urllib.parse import quote

class IsRestaurantOwnerOrStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return True
        restaurant_slug = view.kwargs.get('restaurant_slug')
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
        return request.user and (request.user == restaurant.owner or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (request.user == obj.restaurant.owner or request.user.is_staff)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsRestaurantOwnerOrStaffOrReadOnly]

    def get_queryset(self):
        restaurant_slug = self.kwargs['restaurant_slug']
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
        if self.request.user.is_authenticated:
            if self.request.user == restaurant.owner or self.request.user.is_staff:
                return Order.objects.filter(restaurant=restaurant)
            elif hasattr(self.request.user, 'customer'):
                return Order.objects.filter(restaurant=restaurant, customer=self.request.user.customer)
        return Order.objects.none()

    def perform_create(self, serializer):
        restaurant_slug = self.kwargs['restaurant_slug']
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
        customer = self.request.user.customer if self.request.user.is_authenticated and hasattr(self.request.user, 'customer') else None
        serializer.save(customer=customer, restaurant=restaurant)

    @action(detail=False, methods=['post'], url_path='create-from-cart')
    def create_from_cart(self, request, restaurant_slug=None):
        cart_id = request.data.get('cart_id')
        delivery_price_id = request.data.get('delivery_price_id')

        if not cart_id:
            return Response({"error": "Cart ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(id=cart_id)
            
            # Calculate cart total
            cart_total = sum(item.total_price for item in cart.items.all())

            # Fetch the DeliveryPrice object
            delivery_price = None
            shipping_cost = Decimal('0')
            customer_commune = None
            if delivery_price_id:
                delivery_price = get_object_or_404(DeliveryPrice, id=delivery_price_id)
                shipping_cost = delivery_price.price
                customer_commune = delivery_price.commune

            order_total = cart_total + shipping_cost

            order = Order.objects.create(
                restaurant=cart.restaurant,
                cart=cart,
                payment_method=request.data.get('payment_method'),
                fulfillment_method=request.data.get('fulfillment_method'),
                additional_instructions=request.data.get('additional_instructions'),
                customer_address=request.data.get('address'),
                customer_commune=customer_commune,
                customer_full_name=request.data.get('full_name'),
                customer_phone=request.data.get('phone'),
                customer_email=request.data.get('email'),
                cart_total=cart_total,
                shipping_cost=shipping_cost,
                order_total=order_total
            )

            # Generate WhatsApp message
            # future dev, this might need to be in a conditional for "if resto.wsp_extension"
            whatsapp_message = generate_order_message(order)

            serializer = self.get_serializer(order)
            response_data = serializer.data
            response_data['cart_total'] = str(cart_total)
            response_data['order_total'] = str(order_total)

            return Response({
                'order': response_data,
                'whatsapp_message': whatsapp_message
            }, status=status.HTTP_201_CREATED)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except DeliveryPrice.DoesNotExist:
            return Response({"error": "Delivery price not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None, restaurant_slug=None):
        order = self.get_object()
        if order.customer and order.customer != request.user.customer:
            return Response({"error": "You are not authorized to cancel this order"}, status=status.HTTP_403_FORBIDDEN)
        order.status = 'cancelled'
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)