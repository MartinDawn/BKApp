from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from store.models import Product
from .models import Cart, CartItem, Order


class OrdersTests(APITestCase):
	def setUp(self):
		# Users
		self.buyer = User.objects.create_user(username='buyer', password='pass')
		self.seller1 = User.objects.create_user(username='seller1', password='pass')
		self.seller2 = User.objects.create_user(username='seller2', password='pass')

		# Ensure profiles exist (signal creates them) and set address for buyer
		self.buyer.profile.address = '123 Test St'
		self.buyer.profile.save()

		# Products by different sellers
		self.p1 = Product.objects.create(seller=self.seller1, title='P1', price=100)
		self.p2 = Product.objects.create(seller=self.seller2, title='P2', price=200)

	def test_cart_add_get_patch_delete(self):
		self.client.force_authenticate(user=self.buyer)

		# Add product 1
		r1 = self.client.post('/cart', {'product_id': self.p1.id, 'quantity': 2}, format='json')
		self.assertEqual(r1.status_code, status.HTTP_201_CREATED)

		# Add product 2
		r2 = self.client.post('/cart', {'product_id': self.p2.id, 'quantity': 1}, format='json')
		self.assertEqual(r2.status_code, status.HTTP_201_CREATED)

		# Get cart and verify items and total
		r_get = self.client.get('/cart')
		self.assertEqual(r_get.status_code, status.HTTP_200_OK)
		data = r_get.data
		self.assertIn('items', data)
		self.assertEqual(len(data['items']), 2)
		self.assertEqual(data['total_cart_price'], 100*2 + 200*1)

		# Patch first item (update quantity and note)
		item_id = data['items'][0]['id']
		r_patch = self.client.patch(f'/cart/{item_id}', {'quantity': 3, 'note': 'Please pack'}, format='json')
		self.assertEqual(r_patch.status_code, status.HTTP_200_OK)
		self.assertEqual(r_patch.data['item']['quantity'], 3)
		self.assertEqual(r_patch.data['item']['note'], 'Please pack')

		# Delete second item
		item2_id = data['items'][1]['id']
		r_del = self.client.delete(f'/cart/{item2_id}')
		self.assertEqual(r_del.status_code, status.HTTP_200_OK)

		# Get cart again should have 1 item
		r_get2 = self.client.get('/cart')
		self.assertEqual(len(r_get2.data['items']), 1)

	def test_order_checkout_splits_by_seller_and_clears_cart(self):
		self.client.force_authenticate(user=self.buyer)

		# Add both products to cart
		self.client.post('/cart', {'product_id': self.p1.id, 'quantity': 1}, format='json')
		self.client.post('/cart', {'product_id': self.p2.id, 'quantity': 2}, format='json')

		# Checkout
		resp = self.client.post('/orders', {'address': '123 Checkout Ave'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertIn('Đã tạo', resp.data['message'])

		# Cart should be empty
		cart = Cart.objects.get(user=self.buyer)
		self.assertEqual(cart.items.count(), 0)

		# Orders for buyer should exist (2 sellers => 2 orders)
		orders = Order.objects.filter(buyer=self.buyer)
		self.assertEqual(orders.count(), 2)

	def test_order_list_and_detail_and_permissions(self):
		# Create one order for testing detail and list
		order = Order.objects.create(buyer=self.buyer, seller=self.seller1, shipping_address='Addr', total_price=500)

		# Buyer can view
		self.client.force_authenticate(user=self.buyer)
		r = self.client.get(f'/orders/{order.id}')
		self.assertEqual(r.status_code, status.HTTP_200_OK)

		# Other user cannot view
		other = User.objects.create_user(username='other', password='pass')
		self.client.force_authenticate(user=other)
		r2 = self.client.get(f'/orders/{order.id}')
		self.assertEqual(r2.status_code, status.HTTP_403_FORBIDDEN)

		# Seller list view
		self.client.force_authenticate(user=self.seller1)
		r_list = self.client.get('/orders?role=seller')
		self.assertEqual(r_list.status_code, status.HTTP_200_OK)

	def test_order_status_update_and_product_mark_sold(self):
		# Create order with OrderItem linking to product
		order = Order.objects.create(buyer=self.buyer, seller=self.seller1, shipping_address='Addr', total_price=100)
		from .models import OrderItem
		OrderItem.objects.create(order=order, product=self.p1, price=self.p1.price, quantity=1)

		# Seller updates status to COMPLETED
		self.client.force_authenticate(user=self.seller1)
		r = self.client.patch(f'/orders/{order.id}/status', {'status': 'CM'}, format='json')
		self.assertEqual(r.status_code, status.HTTP_200_OK)

		# Product should be marked as sold
		self.p1.refresh_from_db()
		self.assertEqual(self.p1.status, 'SO')

	def test_cancel_and_return_flows(self):
		# Create order in pending state
		order = Order.objects.create(buyer=self.buyer, seller=self.seller1, shipping_address='Addr', total_price=100, status='PE')

		# Buyer cancels
		self.client.force_authenticate(user=self.buyer)
		r_cancel = self.client.post(f'/orders/{order.id}/cancel')
		self.assertEqual(r_cancel.status_code, status.HTTP_200_OK)
		order.refresh_from_db()
		self.assertEqual(order.status, 'CA')

		# Create delivered order to test return
		order2 = Order.objects.create(buyer=self.buyer, seller=self.seller1, shipping_address='Addr', total_price=100, status='DE')
		self.client.force_authenticate(user=self.buyer)
		r_return = self.client.post(f'/orders/{order2.id}/return')
		self.assertEqual(r_return.status_code, status.HTTP_200_OK)
		order2.refresh_from_db()
		self.assertEqual(order2.status, 'RR')

