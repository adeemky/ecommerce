from rest_framework import serializers
from .models import Category, Brand, Product, Comment
from rest_framework.exceptions import ValidationError, PermissionDenied


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "product", "user", "comment_text", "rating", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate(self, data):
        request = self.context["request"]
        user = request.user
        product = data.get("product")

        if not user.is_staff:
            if "user" in self.initial_data:
                raise PermissionDenied(
                    "You are not allowed to modify the 'user' field."
                )

        if not self.instance:
            if Comment.objects.filter(product=product, user=user).exists():
                raise ValidationError("You have already reviewed this product.")

        return data

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["id"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    number_of_ratings = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "image",
            "in_stock",
            "category",
            "brand",
            "price",
            "average_rating",
            "number_of_ratings",
        ]


class ProductDetailSerializer(ProductSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["comments"]
