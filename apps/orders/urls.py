from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views.order_viewset import OrderViewSet
from apps.orders.views.cart_viewset import CartViewSet

router = DefaultRouter()
router.register(r'order-viewset', OrderViewSet, basename='order')
router.register(r'cart-viewset', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]