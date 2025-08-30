from rest_framework import serializers
from apps.products.models.product_price_option import ProductPriceOption

class ProductPriceOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPriceOption
        fields = ['id', 'name', 'price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(instance.price)
        return representation