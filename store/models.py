# store/models.py
from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
class Category(models.Model):
    """Danh mục sản phẩm (ví dụ: Sách, Đồ điện tử, Nội thất)"""
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    
    # (Trạng thái bán: Còn hàng / Đã bán)
    class Status(models.TextChoices):
        AVAILABLE = 'AV', 'Còn hàng'
        SOLD = 'SO', 'Đã bán'

    # --- THÊM PHẦN NÀY ---
    # Tình trạng sản phẩm (mới/cũ)
    class Condition(models.TextChoices):
        NEW = 'NE', 'Mới 99-100%'
        LIKE_NEW = 'LN', 'Gần như mới (95-98%)'
        USED = 'US', 'Đã qua sử dụng (cũ hơn)'
    # ---------------------

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    image = CloudinaryField('image', folder='products', null=True, blank=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.AVAILABLE)
    
    # --- THÊM TRƯỜNG MỚI NÀY ---
    condition = models.CharField(max_length=2, choices=Condition.choices, default=Condition.USED)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title