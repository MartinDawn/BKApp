
from django.contrib import admin 
from messaging.models import Conversation, Message


# Register your models here.
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.site_header = "Quản trị tin nhắn"
admin.site.site_title = "Quản trị tin nhắn"
admin.site.index_title = "Quản trị tin nhắn"
