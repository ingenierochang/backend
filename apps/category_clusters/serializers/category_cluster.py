from rest_framework import serializers
from apps.category_clusters.models.category_cluster import CategoryCluster
from apps.categories.models.category import Category
from apps.categories.serializers.category import CategorySerializer

class CategoryClusterSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        allow_empty=True
    )
    categories_details = CategorySerializer(source='categories', many=True, read_only=True)

    class Meta:
        model = CategoryCluster
        fields = ['id', 'name', 'categories', 'categories_details', 'image', 'slug', 'order']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure categories field is included in the output
        representation['categories'] = [category.id for category in instance.categories.all()]
        return representation

    def update(self, instance, validated_data):
        """
        Update the instance with the validated data.
        """
        # Update basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        # Update categories if provided
        categories = validated_data.get('categories')
        if categories is not None:
            instance.categories.set(categories)

        return instance
