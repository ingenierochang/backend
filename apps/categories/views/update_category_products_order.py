from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.categories.models.category import Category
from apps.products.models.product import Product
from apps.restaurants.models.restaurant import Restaurant

@api_view(['PUT'])
def update_category_products_order(request, restaurant_slug, category_slug):
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
    category = get_object_or_404(Category, restaurant=restaurant, slug=category_slug)
    order_data = request.data.get('order', [])
    
    # Map of id to product object for quick access
    products_map = {product.id: product for product in Product.objects.filter(id__in=order_data, category=category)}

    try:
        # Update the order of products based on the provided order
        for index, product_id in enumerate(order_data):
            product = products_map.get(product_id)
            if product:
                product.order = index
                product.save()
        return Response({"status": "Order updated successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)