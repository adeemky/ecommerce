from rest_framework import serializers
from .models import Order, OrderItem
from rest_framework.exceptions import PermissionDenied


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "items",
            "total_price",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "total_price",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request_user = self.context["request"].user
        if not request_user.is_staff:
            if "status" in self.initial_data or "user" in self.initial_data:
                raise PermissionDenied(
                    "You are not allowed to modify 'status' or 'user' fields."
                )
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(user=self.context["request"].user)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        order.calculate_total_price()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        instance.calculate_total_price()
        return super().update(instance, validated_data)
