from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission
from django.shortcuts import get_object_or_404
from apps.products.models.product import Product
from apps.products.serializers.product_serializer import ProductSerializer
from apps.restaurants.models.restaurant import Restaurant
from apps.products.utils.process_image import process_image
from collections import OrderedDict
from rest_framework import status
from django.db import transaction
from apps.categories.models.category import Category
import pandas as pd
from django.core.exceptions import PermissionDenied
from rest_framework import permissions
from apps.products.models.product_price_option import ProductPriceOption

class IsRestaurantOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.restaurant.owner == request.user

class ProductViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = ProductSerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly]

    def get_queryset(self):
        restaurant_slug = self.kwargs['restaurant_slug']
        restaurant = self.get_restaurant(restaurant_slug)
        queryset = Product.objects.filter(restaurant=restaurant).select_related('category')
        
        # Apply ordering from query params
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(ordering)
        
        print("hello")
        return queryset

    def get_restaurant(self, restaurant_slug):
        return get_object_or_404(Restaurant, slug=restaurant_slug)

    def get_object(self):
        restaurant = self.get_restaurant(self.kwargs['restaurant_slug'])
        return get_object_or_404(Product, id=self.kwargs['pk'], restaurant=restaurant)

    def check_business_owner(self, request, restaurant):
        if restaurant.owner != request.user:
            self.permission_denied(request)

    def perform_create(self, serializer):
        restaurant = self.get_restaurant(self.kwargs['restaurant_slug'])
        self.check_business_owner(self.request, restaurant)
        
        images = {}
        if 'image' in self.request.FILES:
            images = process_image(self.request.FILES['image'])
        
        product = serializer.save(restaurant=restaurant)
        
        if 'thumbnail' in images:
            product.thumbnail_image.save(images['thumbnail'].name, images['thumbnail'])
        if 'full_size' in images:
            product.detail_image.save(images['full_size'].name, images['full_size'])

        # Clear price and discounted_price if price options are present
        if product.price_options.exists():
            product.price = None
            product.discounted_price = None
            product.save()

    def perform_update(self, serializer):
        product = self.get_object()
        if product.restaurant.owner != self.request.user:
            raise PermissionDenied("You don't have permission to update this product.")
        
        images = {}
        delete_image = self.request.data.get('delete_image', False)
        
        if 'image' in self.request.FILES:
            images = process_image(self.request.FILES['image'])
        
        product = serializer.save()
        
        if delete_image:
            # Delete existing images
            product.thumbnail_image.delete(save=False)
            product.detail_image.delete(save=False)
        
        if 'thumbnail' in images:
            product.thumbnail_image.save(images['thumbnail'].name, images['thumbnail'])
        elif delete_image:
            product.thumbnail_image = None
        
        if 'full_size' in images:
            product.detail_image.save(images['full_size'].name, images['full_size'])
        elif delete_image:
            product.detail_image = None
        
        # Clear price and discounted_price if price options are present
        if product.price_options.exists():
            product.price = None
            product.discounted_price = None
        
        product.save()
    
    @action(detail=False, methods=['get'], url_path="products-categories")
    def products_categories(self, request, restaurant_slug=None):
        restaurant = self.get_restaurant(restaurant_slug)
        categories = OrderedDict()

        # Get products, ordering by category's order and then by product's order
        products = Product.objects.filter(restaurant=restaurant).select_related('category').order_by('category__order', 'order')

        for product in products:
            if not product.category:
                continue
            category_name = product.category.name
            if category_name not in categories:
                categories[category_name] = []
            
            product_data = ProductSerializer(product).data
            
            # Handle price options
            if product.price_options.exists():
                product_data['price'] = None
                product_data['discounted_price'] = None
                product_data['price_options'] = [
                    {'name': po.name, 'price': po.price, "id": po.id}
                    for po in product.price_options.all()
                ]
            
            categories[category_name].append(product_data)

        # Order categories by the order field
        ordered_categories = OrderedDict(
            sorted(categories.items(), key=lambda x: x[1][0]['category']['order'])
        )

        return Response(ordered_categories)
    

    @action(detail=True, methods=['post'], url_path="duplicate-product")
    def duplicate_product(self, request, restaurant_slug=None, pk=None):
        original_product = self.get_object()
        restaurant = self.get_restaurant(restaurant_slug)
        self.check_business_owner(request, restaurant)

        with transaction.atomic():
            # Create a new product as a copy of the original
            new_product = Product.objects.create(
                name=original_product.name,
                description=original_product.description,
                price=original_product.price,
                category=original_product.category,
                restaurant=restaurant,
                active=original_product.active,
                order=original_product.order,
                discounted_price=original_product.discounted_price,
            )

            # Copy images if they exist
            if original_product.thumbnail_image:
                new_product.thumbnail_image.save(
                    original_product.thumbnail_image.name,
                    original_product.thumbnail_image.file,
                    save=False
                )
            if original_product.detail_image:
                new_product.detail_image.save(
                    original_product.detail_image.name,
                    original_product.detail_image.file,
                    save=False
                )

            # Duplicate price options if they exist
            for price_option in original_product.price_options.all():
                ProductPriceOption.objects.create(
                    product=new_product,
                    name=price_option.name,
                    price=price_option.price
                )

            # Clear price and discounted_price if price options exist
            if new_product.price_options.exists():
                new_product.price = None
                new_product.discounted_price = None

            new_product.save()

        serializer = self.get_serializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path="bulk-upload")
    def bulk_upload(self, request, restaurant_slug=None):
        restaurant = self.get_restaurant(restaurant_slug)
        self.check_business_owner(request, restaurant)

        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(excel_file)
            required_columns = ['name', 'category']
            if not all(col in df.columns for col in required_columns):
                return Response({"error": "Excel file is missing required columns. 'name' and 'category' are mandatory."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                for _, row in df.iterrows():
                    category, _ = Category.objects.get_or_create(
                        name=row['category'],
                        restaurant=restaurant
                    )
                    
                    product_data = {
                        'name': row['name'],
                        'category': category,
                        'restaurant': restaurant,
                    }

                    # Handle optional fields
                    optional_fields = ['description', 'price', 'active', 'order', 'discounted_price']
                    for field in optional_fields:
                        if field in row and pd.notna(row[field]) and row[field] != 'nan':
                            if field in ['price', 'discounted_price']:
                                try:
                                    product_data[field] = float(row[field])
                                except ValueError:
                                    continue  # Skip this field if it's not a valid float
                            elif field == 'active':
                                product_data[field] = str(row[field]).lower() in ['true', '1', 'yes']
                            elif field == 'order':
                                try:
                                    product_data[field] = int(row[field])
                                except ValueError:
                                    continue  # Skip this field if it's not a valid integer
                            else:
                                product_data[field] = row[field]

                    product = Product.objects.create(**product_data)

                    # Handle price options if present
                    if 'price_options' in row and pd.notna(row['price_options']):
                        price_options = row['price_options'].split(',')
                        for option in price_options:
                            name, price = option.split(':')
                            ProductPriceOption.objects.create(
                                product=product,
                                name=name.strip(),
                                price=float(price.strip())
                            )
                        # Clear price and discounted_price if price options exist
                        product.price = None
                        product.discounted_price = None
                        product.save()

            return Response({"message": "Products uploaded successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)