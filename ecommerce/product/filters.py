from django_filters import rest_framework as filters
from django.db.models import Avg
from .models import Product, Category

""" /api/products/?id=&name=&brand=&category=&price=&in_stock=&price_min=&price_max=&average_rating_min= """

class ProductFilter(filters.FilterSet):
    id = filters.NumberFilter()
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    brand = filters.CharFilter(field_name="brand__name", lookup_expr="icontains")
    category = filters.CharFilter(method="filter_category")
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")
    average_rating_min = filters.NumberFilter(method="filter_average_rating")
    in_stock = filters.BooleanFilter(field_name="in_stock")

    class Meta:
        model = Product
        fields = ["id", "name", "brand", "category", "in_stock"]

    def filter_category(self, queryset, name, value):
        try:
            category = Category.objects.get(name__iexact=value)
            descendants = category.get_descendants(include_self=True)
            return queryset.filter(category__in=descendants)
        except Category.DoesNotExist:
            return queryset.none()

    def filter_average_rating(self, queryset, name, value):
        return queryset.annotate(avg_rating=Avg("comments__rating")).filter(avg_rating__gte=value)

