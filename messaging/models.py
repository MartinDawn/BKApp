from django.db import models
from django.contrib.auth.models import User
from store.models import Product  # Import Product để gửi kèm tin nhắn
from cloudinary.models import CloudinaryField

class Conversation(models.Model):
    """Cuộc trò chuyện giữa 2 người"""
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conv_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conv_p2')
    
    updated_at = models.DateTimeField(auto_now=True) # Để sắp xếp chat mới nhất lên đầu

    class Meta:
        unique_together = ('participant1', 'participant2') # 2 người chỉ có 1 cuộc hội thoại duy nhất

    def __str__(self):
        return f"Chat {self.participant1.username} & {self.participant2.username}"

class Message(models.Model):
    """Tin nhắn chi tiết"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    
    content = models.TextField(blank=True, null=True) # Nội dung text
    image = CloudinaryField('image', folder='chat_images', null=True, blank=True) # Ảnh gửi kèm
    
    # Optional: Gửi kèm link sản phẩm để người mua biết đang hỏi về cái gì
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.sender.username} at {self.created_at}"