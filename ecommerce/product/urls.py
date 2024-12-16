from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BrandViewSet, ProductViewSet, CommentViewSet

router = DefaultRouter()
router.register(r"category", CategoryViewSet)
router.register(r"brands", BrandViewSet)
router.register(r"products", ProductViewSet)
router.register(r"comments", CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
