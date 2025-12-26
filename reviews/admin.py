from django.contrib import admin

from reviews.models import Review

# Register your models here.
admin.site.site_header = "Quản trị đánh giá sản phẩm"
admin.site.site_title = "Quản trị đánh giá sản phẩm"
admin.site.index_title = "Quản trị đánh giá sản phẩm"
admin.site.register(Review)