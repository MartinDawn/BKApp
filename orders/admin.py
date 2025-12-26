from django.contrib import admin

from orders.models import Cart, CartItem, Order, OrderItem

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.site_header = "Quản trị đơn hàng"
admin.site.site_title = "Quản trị đơn hàng"
admin.site.index_title = "Quản trị đơn hàng"
admin.site.register(Cart)
admin.site.register(CartItem)