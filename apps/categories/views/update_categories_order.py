from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.categories.models.category import Category
from apps.restaurants.models.restaurant import Restaurant

@api_view(['PUT'])
def update_categories_order(request, restaurant_slug):
    # TODO: add permissions
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
    order_data = request.data.get('order', [])
    
    # Map of id to category cluster object for quick access
    categories_map = {category.id: category for category in Category.objects.filter(id__in=order_data, restaurant=restaurant)}

    try:
        # Update the order of category clusters based on the provided order
        for index, category_id in enumerate(order_data):
            category = categories_map.get(category_id)
            print("category")
            if category:
                category.order = index
                
                category.save()
                print("saved")
        return Response({"status": "Order updated successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
