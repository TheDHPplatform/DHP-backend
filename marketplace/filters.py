import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    
    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'search', 'is_featured']