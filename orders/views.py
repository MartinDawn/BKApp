from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product
from .serializers import CartItemSerializer, CartSerializer, OrderSerializer

# --- PHẦN GIỎ HÀNG (CART) ---

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lấy giỏ hàng"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        """Thêm vào giỏ"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        if product.status == 'SO': # Kiểm tra nếu đã bán
             return Response({"error": "Sản phẩm đã hết hàng"}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Nếu đã có trong giỏ thì tăng số lượng
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        return Response({"message": "Đã thêm vào giỏ hàng"}, status=201)

class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        """Cập nhật số lượng hoặc ghi chú"""
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        if 'quantity' in request.data:
            cart_item.quantity = request.data['quantity']
        if 'note' in request.data:
            cart_item.note = request.data['note']
            
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response({"message": "Cập nhật thành công", "item": serializer.data})

    def delete(self, request, item_id):
        """Xóa khỏi giỏ"""
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return Response({"message": "Đã xóa sản phẩm"})


# --- PHẦN ĐƠN HÀNG (ORDER) ---

class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Lấy danh sách đơn hàng (vừa là người mua, vừa là người bán)"""
        role = request.query_params.get('role') # ?role=seller hoặc ?role=buyer
        
        if role == 'seller':
            orders = Order.objects.filter(seller=request.user).order_by('-created_at')
        else:
            orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
            
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Tạo đơn hàng (Checkout) - Logic tách đơn theo người bán"""
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            return Response({"error": "Giỏ hàng trống"}, status=400)

        # Lấy địa chỉ: Ưu tiên địa chỉ gửi lên, nếu không thì lấy trong Profile
        address = request.data.get('address') or user.profile.address
        if not address:
             return Response({"error": "Chưa có địa chỉ giao hàng"}, status=400)

        # Nhóm sản phẩm theo người bán (Seller)
        orders_by_seller = {}
        for item in cart_items:
            seller_id = item.product.seller.id
            if seller_id not in orders_by_seller:
                orders_by_seller[seller_id] = []
            orders_by_seller[seller_id].append(item)

        created_orders = []

        try:
            with transaction.atomic():
                for seller_id, items in orders_by_seller.items():
                    # Tính tổng tiền cho đơn hàng con này
                    total_price = sum(item.product.price * item.quantity for item in items)
                    
                    # 1. Tạo Order
                    order = Order.objects.create(
                        buyer=user,
                        seller_id=seller_id,
                        shipping_address=address,
                        total_price=total_price,
                        status=Order.Status.PENDING
                    )
                    
                    # 2. Tạo OrderItem
                    for item in items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            price=item.product.price,
                            quantity=item.quantity
                        )
                    
                    created_orders.append(order)
                
                # 3. Xóa sạch giỏ hàng
                cart.items.all().delete()
                
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({"message": f"Đã tạo {len(created_orders)} đơn hàng."}, status=201)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Xem chi tiết đơn hàng"""
        order = get_object_or_404(Order, pk=pk)
        
        # Chỉ người mua hoặc người bán mới được xem
        if request.user != order.buyer and request.user != order.seller:
            return Response({"error": "Không có quyền truy cập"}, status=403)
            
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class OrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        """Cập nhật trạng thái (Duyệt, Giao, Hoàn thành)"""
        # Logic: Thường chỉ Seller mới được update các trạng thái này
        order = get_object_or_404(Order, pk=pk, seller=request.user)
        new_status = request.data.get('status')
        
        if new_status in Order.Status.values:
            order.status = new_status
            order.save()
            
            # Nếu Hoàn Thành -> Set sản phẩm thành Đã Bán
            if new_status == Order.Status.COMPLETED:
                for item in order.items.all():
                    item.product.status = 'SO' # SO = Sold
                    item.product.save()

            return Response({"message": "Đã cập nhật trạng thái"})
        return Response({"error": "Trạng thái không hợp lệ"}, status=400)

class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Hủy đơn hàng"""
        order = get_object_or_404(Order, pk=pk)
        
        # Buyer hoặc Seller đều được hủy nếu đơn chưa giao
        if request.user not in [order.buyer, order.seller]:
             return Response({"error": "Không có quyền"}, status=403)

        if order.status in ['PE', 'CO']: # Pending hoặc Confirmed
            order.status = Order.Status.CANCELED
            order.save()
            return Response({"message": "Đã hủy đơn hàng"})
        
        return Response({"error": "Đơn hàng đang giao, không thể hủy"}, status=400)

class ReturnOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Yêu cầu trả hàng"""
        order = get_object_or_404(Order, pk=pk, buyer=request.user)
        
        if order.status == Order.Status.DELIVERED: # Phải nhận hàng rồi mới trả được
            order.status = Order.Status.RETURN_REQUESTED
            order.save()
            return Response({"message": "Đã gửi yêu cầu trả hàng"})
        
        return Response({"error": "Chỉ có thể trả hàng khi trạng thái là Đang giao/Đã nhận"}, status=400)