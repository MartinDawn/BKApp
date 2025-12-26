from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    reviewer_avatar = serializers.SerializerMethodField()
    
    # Hiển thị tên sản phẩm đã mua để tăng độ uy tín
    # Giả sử Order có nhiều item, ta lấy tên item đầu tiên làm đại diện
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'order', 'reviewer', 'reviewer_name', 'reviewer_avatar', 
                  'reviewee', 'rating', 'comment', 'image', 'created_at', 'product_info']
        read_only_fields = ['reviewer', 'reviewee'] # Các trường này tự lấy từ Order

    def get_reviewer_avatar(self, obj):
        # if hasattr(obj.reviewer, 'profile') and obj.reviewer.profile.avatar:
        #     return obj.reviewer.profile.avatar.url
        return ""

    def get_product_info(self, obj):
        # Lấy item đầu tiên trong đơn hàng để hiển thị: "Đã mua: iPhone 12..."
        first_item = obj.order.items.first()
        if first_item:
            return f"{first_item.product.title}"
        return "Sản phẩm đã mua"    