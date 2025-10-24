# store/serializers.py
from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    # seller = serializers.ReadOnlyField(source='seller.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    
    # --- THÊM DÒNG NÀY ---
    # Trả về tên hiển thị (ví dụ: "Đã qua sử dụng")
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'category', 'category_name', 'title', 
            'description', 'price', 'image', 'status', 'created_at',
            
            # --- THÊM 2 TRƯỜNG NÀY ---
            'condition',         # Để GHI (ví dụ: 'US')
            'condition_display'  # Để ĐỌC (ví dụ: 'Đã qua sử dụng')
        ]

    # Hàm to_representation (để sửa link ảnh) vẫn giữ nguyên
    def to_representation(self, instance):
        data = super().to_representation(instance)
        image = instance.image
        if image:
            data['image'] = image.url
        return data