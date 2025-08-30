from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from apps.restaurants.models.restaurant import Restaurant
from apps.category_clusters.models.category_cluster import CategoryCluster
from apps.category_clusters.serializers.category_cluster import CategoryClusterSerializer

class CategoryClusterView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_restaurant(self, restaurant_slug):
        return get_object_or_404(Restaurant, slug=restaurant_slug)

    def get_object(self, restaurant, category_cluster_id):
        return get_object_or_404(CategoryCluster, id=category_cluster_id, restaurant=restaurant)

    def get(self, request, restaurant_slug=None, category_cluster_id=None):
        restaurant = self.get_restaurant(restaurant_slug)
        if category_cluster_id:
            category_cluster = self.get_object(restaurant, category_cluster_id)
            serializer = CategoryClusterSerializer(category_cluster)
        else:
            category_clusters = CategoryCluster.objects.filter(restaurant=restaurant).order_by('order')
            serializer = CategoryClusterSerializer(category_clusters, many=True)
        return Response(serializer.data)

    def post(self, request, restaurant_slug=None):
        restaurant = self.get_restaurant(restaurant_slug)
        serializer = CategoryClusterSerializer(data=request.data)
        if serializer.is_valid():
            category_cluster = serializer.save(restaurant=restaurant)
            # Handle many-to-many relationships explicitly
            categories = request.data.get('categories', [])
            if categories:
                category_cluster.categories.set(categories)
            return Response(CategoryClusterSerializer(category_cluster).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, restaurant_slug=None, category_cluster_id=None):
        restaurant = self.get_restaurant(restaurant_slug)
        category_cluster = self.get_object(restaurant, category_cluster_id)
        serializer = CategoryClusterSerializer(category_cluster, data=request.data, partial=False)
        if serializer.is_valid():
            category_cluster = serializer.save()
            # Handle many-to-many relationships explicitly
            categories = request.data.get('categories', [])
            if categories:
                category_cluster.categories.set(categories)
            return Response(CategoryClusterSerializer(category_cluster).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, restaurant_slug=None, category_cluster_id=None):
        restaurant = self.get_restaurant(restaurant_slug)
        category_cluster = self.get_object(restaurant, category_cluster_id)
        serializer = CategoryClusterSerializer(category_cluster, data=request.data, partial=True)
        if serializer.is_valid():
            category_cluster = serializer.save()
            # Handle many-to-many relationships explicitly
            categories = request.data.getlist('categories', [])
            print("categories: ", categories)
            if categories is not None:  # Handle the case where categories may not be included in the PATCH request
                category_cluster.categories.set(categories)
            return Response(CategoryClusterSerializer(category_cluster).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, restaurant_slug=None, category_cluster_id=None):
        restaurant = self.get_restaurant(restaurant_slug)
        category_cluster = self.get_object(restaurant, category_cluster_id)
        category_cluster.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
