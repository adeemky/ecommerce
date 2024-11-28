from rest_framework import serializers
from .models import Category, Brand, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    # brand = serializers.CharField(source="brand.name")
    # category = CategorySerializer()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "is_digital", "brand", "category"]
        read_only_fields = ["id"]
