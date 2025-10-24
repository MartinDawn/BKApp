# store/views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .filters import ProductFilter # <-- 1. Import bộ lọc
class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Quyền tùy chỉnh: Chỉ cho phép người đăng (seller)
    mới được phép chỉnh sửa hoặc xóa sản phẩm.
    """
    def has_object_permission(self, request, view, obj):
        # Ai cũng có thể xem (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Chỉ chủ sở hữu (seller) mới được phép sửa (PUT, PATCH) hoặc xóa (DELETE)
        return obj.seller == request.user
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10                 # Mặc định 10 sản phẩm/trang
    page_size_query_param = 'page_size' # Cho phép client tự chọn (ví dụ: ?page_size=20)
    max_page_size = 100            # Tối đa 100 sản phẩm/trang
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint để XEM danh sách các danh mục.
    (ReadOnly: chỉ cho phép GET, không cho POST/PUT/DELETE)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny] # Ai cũng được xem

class ProductViewSet(viewsets.ModelViewSet):
    """
    API cho phép TẠO, XEM, SỬA, XÓA sản phẩm
    Hỗ trợ: Lọc, Tìm kiếm, Sắp xếp, Phân trang.
    """
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    
    # --- THÊM CÁC DÒNG CẤU HÌNH NÀY ---
    
    # 4. Kích hoạt Phân trang
    pagination_class = StandardResultsSetPagination

    # 5. Kích hoạt các bộ lọc
    filter_backends = [
        DjangoFilterBackend,     # Cho ?category=, ?price_min=...
        filters.SearchFilter,    # Cho ?search=... (tham số 'q' của bạn)
        filters.OrderingFilter   # Cho ?ordering=... (tham số 'sort' của bạn)
    ]
    
    # 6. Chỉ định lớp FilterSet
    filterset_class = ProductFilter

    # 7. Cấu hình cho ?search=... (tham số 'q' của bạn)
    # DRF dùng 'search' thay vì 'q', nhưng nó hoạt động y hệt
    search_fields = ['title', 'description']

    # 8. Cấu hình cho ?ordering=... (tham số 'sort' của bạn)
    # (DRF dùng 'ordering' thay vì 'sort')
    ordering_fields = ['created_at', 'price']
    
    # --- PHẦN DƯỚI GIỮ NGUYÊN ---
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)