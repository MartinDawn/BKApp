# store/filters.py
import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    # Lọc giá: ?price_min=...
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    # Lọc giá: ?price_max=...
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    seller_username = django_filters.CharFilter(
        field_name='seller__username',  # Lọc qua trường 'username' của 'seller'
        lookup_expr='iexact'            # 'iexact' = lọc không phân biệt hoa thường
    )
    class Meta:
        model = Product
        # Thêm 'category' và 'condition' vào đây
        # DRF sẽ tự động tạo bộ lọc cho chúng
        fields = ['category', 
                  'condition', 
                  'price_min', 
                  'price_max',
                  'seller',
                #   'seller_username',
                  ]