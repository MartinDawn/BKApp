from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationListSerializer, MessageSerializer
from django.contrib.auth.models import User

# 1. Lấy danh sách cuộc trò chuyện (Inbox)
class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Lấy các chat mà user là p1 HOẶC p2
        chats = Conversation.objects.filter(
            Q(participant1=request.user) | Q(participant2=request.user)
        ).order_by('-updated_at')
        
        serializer = ConversationListSerializer(chats, many=True, context={'request': request})
        return Response(serializer.data)

# 2. Quản lý tin nhắn trong 1 cuộc hội thoại
class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        """Lấy lịch sử tin nhắn"""
        conversation = get_object_or_404(Conversation, id=chat_id)
        
        # Bảo mật: Chỉ người trong cuộc mới xem được
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response({"error": "Không có quyền truy cập"}, status=403)
            
        messages = conversation.messages.order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, chat_id):
        """Gửi tin nhắn mới"""
        conversation = get_object_or_404(Conversation, id=chat_id)
        
        if request.user not in [conversation.participant1, conversation.participant2]:
            return Response({"error": "Không có quyền gửi tin"}, status=403)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(conversation=conversation, sender=request.user)
            
            # Update thời gian chat để nó nổi lên đầu danh sách
            conversation.save() 
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# 3. Đánh dấu đã đọc
class MarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chat_id):
        conversation = get_object_or_404(Conversation, id=chat_id)
        
        # Update tất cả tin nhắn mả người gửi KHÔNG PHẢI là mình -> thành đã đọc
        conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        
        return Response({"message": "Đã đánh dấu đã đọc"})

# 4. (BỔ SUNG) Bắt đầu chat từ trang sản phẩm
class StartChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Input: { "target_user_id": 123 }
        Logic: Tìm xem đã có chat với user 123 chưa? Nếu có trả về ID, chưa thì tạo mới.
        """
        target_id = request.data.get('target_user_id')
        if not target_id:
            return Response({"error": "Thiếu target_user_id"}, status=400)
            
        if int(target_id) == request.user.id:
            return Response({"error": "Không thể chat với chính mình"}, status=400)

        target_user = get_object_or_404(User, id=target_id)

        # Tìm conversation cũ (không quan trọng ai là p1, p2)
        chat = Conversation.objects.filter(
            (Q(participant1=request.user) & Q(participant2=target_user)) |
            (Q(participant1=target_user) & Q(participant2=request.user))
        ).first()

        if chat:
            return Response({"chat_id": chat.id, "message": "Chat cũ đã tồn tại"})
        
        # Tạo mới
        new_chat = Conversation.objects.create(participant1=request.user, participant2=target_user)
        return Response({"chat_id": new_chat.id, "message": "Đã tạo chat mới"}, status=201)