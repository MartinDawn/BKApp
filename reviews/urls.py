from django.urls import path
from .views import CreateReviewView, SellerReviewListView, ReviewStatsView

urlpatterns = [
    # POST: Tạo review
    path('reviews', CreateReviewView.as_view(), name='create-review'),
    
    # GET: Xem review của user {id}
    path('users/<int:seller_id>/reviews', SellerReviewListView.as_view(), name='seller-reviews'),
    
    # GET: Xem thống kê sao của user {id}
    path('reviews/stats/<int:seller_id>', ReviewStatsView.as_view(), name='review-stats'),
]