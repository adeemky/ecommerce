from rest_framework import viewsets, permissions
from .models import Category, Brand, Product, Comment
from .serializers import CategorySerializer, BrandSerializer, ProductSerializer, ProductDetailSerializer, CommentSerializer
from .permissions import ProductPermission, IsCommentUserOrReadOnly
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAdminUser]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [ProductPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ["name", "price"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCommentUserOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get("product")
        user_id = self.request.query_params.get("user")

        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset
