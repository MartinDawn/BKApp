# store/admin.py
from django.contrib import admin
from .models import Category, Product

# Đăng ký model để chúng hiển thị trên trang admin
admin.site.register(Category)
admin.site.register(Product)