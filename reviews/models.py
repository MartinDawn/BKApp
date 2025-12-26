from django.db import models
from django.contrib.auth.models import User
from orders.models import Order
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

class Review(models.Model):
    # Liên kết 1-1 với Order: Một đơn hàng chỉ có 1 review duy nhất
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written') # Người mua
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received') # Người bán
    
    rating = models.PositiveIntegerField(default=5) # 1 đến 5 sao
    comment = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', folder='reviews', null=True, blank=True) # Ảnh thực tế sản phẩm nhận được
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} rated {self.reviewee.username} {self.rating}*"

# --- TỰ ĐỘNG CẬP NHẬT RATING CHO NGƯỜI BÁN ---
@receiver(post_save, sender=Review)
def update_seller_rating(sender, instance, created, **kwargs):
    """
    Mỗi khi có Review mới, tự động tính lại trung bình sao cho người bán (Profile)
    """
    if created:
        seller_profile = instance.reviewee.profile
        
        # Tính toán lại
        stats = Review.objects.filter(reviewee=instance.reviewee).aggregate(
            avg_rating=Avg('rating'),
            count=models.Count('id')
        )
        
        # Cập nhật vào bảng Profile (để hiển thị nhanh mà không cần query lại bảng Review)
        seller_profile.rating = round(stats['avg_rating'] or 0, 1)
        seller_profile.num_reviews = stats['count'] or 0
        seller_profile.save()