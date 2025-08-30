from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, MyRestaurant

router = DefaultRouter()
router.register(r'', RestaurantViewSet, basename='restaurant')

urlpatterns = [
    path('my-restaurant/', MyRestaurant.as_view(), name='owner-restaurant'), # on top


    path('<str:restaurant_slug>/products/', include('apps.products.urls')),
    path('<str:restaurant_slug>/categories/', include('apps.categories.urls')),
    path('<str:restaurant_slug>/category_clusters/', include('apps.category_clusters.urls')),

    path('<str:restaurant_slug>/orders/', include('apps.orders.urls')), # orders and carts


    path('', include(router.urls)),
]
