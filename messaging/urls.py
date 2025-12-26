from django.urls import path
from .views import ChatListView, MessageListCreateView, MarkReadView, StartChatView

urlpatterns = [
    # Lấy danh sách chat (Inbox)
    path('chats', ChatListView.as_view(), name='chat-list'),
    
    # Lấy message / Gửi message
    path('chats/<int:chat_id>/messages', MessageListCreateView.as_view(), name='message-list-create'),
    
    # Đánh dấu đã đọc
    path('chats/<int:chat_id>/read', MarkReadView.as_view(), name='chat-mark-read'),
    
    # API phụ trợ: Bắt đầu chat với một người bán (dùng khi bấm nút "Chat" ở trang Product)
    path('chats/start', StartChatView.as_view(), name='chat-start'),
]