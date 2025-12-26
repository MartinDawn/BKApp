from django.urls import path
from .views import (
    CartView, CartItemDetailView,
    OrderListCreateView, OrderDetailView,
    OrderStatusView, CancelOrderView, ReturnOrderView
)

urlpatterns = [
    # Cart Endpoints
    path('cart', CartView.as_view(), name='cart-list'),
    path('cart/<int:item_id>', CartItemDetailView.as_view(), name='cart-detail'),

    # Order Endpoints
    path('orders', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status', OrderStatusView.as_view(), name='order-status'),
    path('orders/<int:pk>/cancel', CancelOrderView.as_view(), name='order-cancel'),
    path('orders/<int:pk>/return', ReturnOrderView.as_view(), name='order-return'),
]