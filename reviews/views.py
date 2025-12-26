from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg
from .models import Review
from .serializers import ReviewSerializer
from orders.models import Order
from django.contrib.auth.models import User

# 1. Tạo Review mới
class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment')
        
        # 1. Kiểm tra đơn hàng tồn tại
        order = get_object_or_404(Order, id=order_id)
        
        # 2. Kiểm tra quyền: Chỉ người mua mới được review
        if order.buyer != request.user:
            return Response({"error": "Bạn không phải người mua đơn hàng này"}, status=403)
            
        # 3. Kiểm tra trạng thái: Phải hoàn thành mới được review
        if order.status != 'CM': # CM = COMPLETED (Check model Order của bạn)
            return Response({"error": "Đơn hàng chưa hoàn thành, chưa thể đánh giá"}, status=400)
            
        # 4. Kiểm tra trùng lặp: Đơn này đã review chưa?
        if hasattr(order, 'review'):
            return Response({"error": "Đơn hàng này đã được đánh giá rồi"}, status=400)

        # 5. Lưu Review
        # Lưu ý: reviewee (người được đánh giá) chính là seller của đơn hàng
        review = Review.objects.create(
            order=order,
            reviewer=request.user,
            reviewee=order.seller,
            rating=rating,
            comment=comment
        )
        
        # Xử lý ảnh nếu có (tùy code upload của bạn)
        if 'image' in request.FILES:
            review.image = request.FILES['image']
            review.save()

        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=201)

# 2. Lấy danh sách Review của một Seller
class SellerReviewListView(APIView):
    def get(self, request, seller_id):
        # Lấy tất cả review mà người này là "reviewee"
        reviews = Review.objects.filter(reviewee_id=seller_id).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

# 3. Lấy thống kê chi tiết (Số sao trung bình, phân bố 1-5 sao)
class ReviewStatsView(APIView):
    def get(self, request, seller_id):
        reviews = Review.objects.filter(reviewee_id=seller_id)
        
        total_reviews = reviews.count()
        if total_reviews == 0:
            return Response({
                "avg_rating": 0,
                "total_reviews": 0,
                "distribution": {1:0, 2:0, 3:0, 4:0, 5:0}
            })
            
        # Tính điểm trung bình
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        
        # Tính phân bố (Có bao nhiêu 5 sao, bao nhiêu 4 sao...)
        # Cách nhanh: Dùng Python loop hoặc query group by
        distribution = {1:0, 2:0, 3:0, 4:0, 5:0}
        stats = reviews.values('rating').annotate(count=Count('rating'))
        
        for item in stats:
            r = item['rating']
            if r in distribution:
                distribution[r] = item['count']
                
        return Response({
            "avg_rating": round(avg_rating, 1),
            "total_reviews": total_reviews,
            "distribution": distribution
        })