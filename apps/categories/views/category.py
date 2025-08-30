from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from apps.categories.models.category import Category
from apps.categories.serializers.category import CategorySerializer
from apps.restaurants.models.restaurant import Restaurant

class CategoryView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_restaurant(self, restaurant_slug):
        """
        Retrieve the Restaurant object or return a 404 error if not found.
        """
        return get_object_or_404(Restaurant, slug=restaurant_slug)

    def get_object(self, restaurant, category_id):
        """
        Retrieve the Category object or return a 404 error if not found.
        """
        return get_object_or_404(Category, id=category_id, restaurant=restaurant)

    def get(self, request, restaurant_slug=None, category_id=None):
        """
        Handle GET request to retrieve a single category by its ID or list all categories within a restaurant.
        """
        if restaurant_slug:
            restaurant = self.get_restaurant(restaurant_slug)
            if category_id:
                category = self.get_object(restaurant, category_id)
                serializer = CategorySerializer(category)
            else:
                categories = Category.objects.filter(restaurant=restaurant).order_by("order")
                serializer = CategorySerializer(categories, many=True)
        else:
            return Response({"detail": "Restaurant ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            # if category_id:
            #     category = self.get_object(None, category_id)
            #     serializer = CategorySerializer(category)
            # else:
            #     categories = Category.objects.all()
            #     serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, restaurant_slug=None):
        """
        Handle POST request to create a new category within a restaurant.
        """
        if restaurant_slug:
            restaurant = self.get_restaurant(restaurant_slug)
            if not restaurant.owner == request.user:
                return Response({"detail": "You do not have permission to add categories to this restaurant."}, status=status.HTTP_403_FORBIDDEN)

            serializer = CategorySerializer(data=request.data, context={'user': request.user, 'restaurant': restaurant})
            if serializer.is_valid():
                serializer.save(restaurant=restaurant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Restaurant ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, restaurant_slug=None, category_id=None):
        """
        Handle PUT request to update an existing category within a restaurant.
        """
        if restaurant_slug:
            restaurant = self.get_restaurant(restaurant_slug)
            category = self.get_object(restaurant, category_id)
            if restaurant.owner != request.user:
                return Response({"detail": "You do not have permission to edit this category."}, status=status.HTTP_403_FORBIDDEN)

            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        else:
            return Response({"detail": "Restaurant ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, restaurant_slug=None, category_id=None):
        """
        Handle PATCH request to partially update an existing category within a restaurant.
        """
        return self.put(request, restaurant_slug, category_id)

    def delete(self, request, restaurant_slug=None, category_id=None):
        """
        Handle DELETE request to delete a category within a restaurant.
        """
        if restaurant_slug:
            restaurant = self.get_restaurant(restaurant_slug)
            category = self.get_object(restaurant, category_id)
            if restaurant.owner != request.user:
                return Response({"detail": "You do not have permission to delete this category."}, status=status.HTTP_403_FORBIDDEN)

            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Restaurant ID is required."}, status=status.HTTP_400_BAD_REQUEST)
