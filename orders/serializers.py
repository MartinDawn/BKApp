from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from store.models import Product

# Serializer phụ để hiện thông tin Product gọn gàng trong giỏ
class MiniProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'image', 'seller_name', 'status']

# --- CART SERIALIZERS ---
class CartItemSerializer(serializers.ModelSerializer):
    product = MiniProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True) 

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'note']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_cart_price']

    def get_total_cart_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

# --- ORDER SERIALIZERS ---
class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'product_image', 'price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'buyer_name', 'seller', 'seller_name', 
                  'status', 'shipping_address', 'total_price', 'items', 'created_at']