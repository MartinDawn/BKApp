from django.db import models
from django.contrib.auth.models import User
from store.models import Product  # Import Product từ app store cũ

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    note = models.TextField(blank=True, null=True) # Ghi chú cho người bán (nếu cần)

    class Meta:
        unique_together = ('cart', 'product')

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PE', 'Chờ xác nhận'
        CONFIRMED = 'CO', 'Đã xác nhận'
        DELIVERED = 'DE', 'Đang giao'
        COMPLETED = 'CM', 'Hoàn thành'
        CANCELED = 'CA', 'Đã hủy'
        RETURN_REQUESTED = 'RR', 'Yêu cầu trả hàng'
        RETURNED = 'RE', 'Đã trả hàng'

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_bought')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_sold')
    
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PENDING)
    shipping_address = models.TextField()
    total_price = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=0) # Lưu giá lúc mua
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Item {self.id} for Order {self.order.id}"