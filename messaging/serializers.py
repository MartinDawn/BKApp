from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message
from store.models import Product

# Serializer nhỏ cho Product (nếu tin nhắn có đính kèm sp)
class MiniProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'image']

# Serializer cho Tin nhắn chi tiết
class MessageSerializer(serializers.ModelSerializer):
    product = MiniProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'sender_avatar', 'content', 'image', 'product', 'product_id', 'is_read', 'created_at']

    def get_sender_avatar(self, obj):
        # Giả sử User có Profile, nếu không có thì trả về None
        # if hasattr(obj.sender, 'profile') and obj.sender.profile.avatar:
        #     return obj.sender.profile.avatar.url
        return ""

# Serializer cho Danh sách cuộc hội thoại (Inbox)
class ConversationListSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'other_user', 'last_message', 'updated_at']

    def get_other_user(self, obj):
        """Lấy thông tin người kia (không phải người đang request)"""
        request = self.context.get('request')
        if obj.participant1 == request.user:
            target = obj.participant2
        else:
            target = obj.participant1
            
        return {
            "id": target.id,
            "username": target.username,
            # "avatar": target.profile.avatar.url if hasattr(target, 'profile') and target.profile.avatar else ""
        }

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                "content": last_msg.content if last_msg.content else "[Hình ảnh]",
                "is_read": last_msg.is_read,
                "sender_id": last_msg.sender.id,
                "created_at": last_msg.created_at
            }
        return None