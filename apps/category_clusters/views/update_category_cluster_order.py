from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.category_clusters.models.category_cluster import CategoryCluster
from apps.restaurants.models.restaurant import Restaurant

@api_view(['PUT'])
def update_category_cluster_order(request, restaurant_slug):
    # TODO: add permissions
    restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
    order_data = request.data.get('order', [])
    
    # Map of id to category cluster object for quick access
    category_cluster_map = {cluster.id: cluster for cluster in CategoryCluster.objects.filter(id__in=order_data, restaurant=restaurant)}

    try:
        # Update the order of category clusters based on the provided order
        for index, category_cluster_id in enumerate(order_data):
            category_cluster = category_cluster_map.get(category_cluster_id)
            print("category_cluster")
            if category_cluster:
                category_cluster.order = index
                
                category_cluster.save()
                print("saved")
        return Response({"status": "Order updated successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
