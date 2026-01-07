from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from store.models import Product
from orders.models import Order, OrderItem
from .models import Review


class ReviewsTests(APITestCase):
	def setUp(self):
		self.buyer = User.objects.create_user(username='buyer', password='pass')
		self.seller = User.objects.create_user(username='seller', password='pass')
		self.other = User.objects.create_user(username='other', password='pass')

		# Ensure buyer has address via Profile (signal creates Profile)
		self.buyer.profile.address = 'Home'
		self.buyer.profile.save()

		# Product and completed order
		self.product = Product.objects.create(seller=self.seller, title='Prod', price=150)
		self.order = Order.objects.create(buyer=self.buyer, seller=self.seller, shipping_address='Addr', total_price=150, status='CM')
		OrderItem.objects.create(order=self.order, product=self.product, price=self.product.price, quantity=1)

	def test_create_review_success_updates_profile(self):
		self.client.force_authenticate(user=self.buyer)
		resp = self.client.post('/reviews', {'order_id': self.order.id, 'rating': 4, 'comment': 'Good'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(int(resp.data['rating']), 4)
		self.assertEqual(resp.data['reviewer_name'], self.buyer.username)

		# Profile of seller should be updated by signal
		self.seller.profile.refresh_from_db()
		self.assertEqual(self.seller.profile.num_reviews, 1)
		self.assertEqual(self.seller.profile.rating, 4.0)

	def test_create_review_forbidden_if_not_buyer(self):
		self.client.force_authenticate(user=self.other)
		resp = self.client.post('/reviews', {'order_id': self.order.id, 'rating': 5}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

	def test_create_review_bad_if_order_not_completed(self):
		pending = Order.objects.create(buyer=self.buyer, seller=self.seller, shipping_address='A', total_price=100, status='PE')
		self.client.force_authenticate(user=self.buyer)
		resp = self.client.post('/reviews', {'order_id': pending.id, 'rating': 3}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_create_review_duplicate(self):
		# first review
		self.client.force_authenticate(user=self.buyer)
		r1 = self.client.post('/reviews', {'order_id': self.order.id, 'rating': 5}, format='json')
		self.assertEqual(r1.status_code, status.HTTP_201_CREATED)

		# second attempt should fail
		r2 = self.client.post('/reviews', {'order_id': self.order.id, 'rating': 4}, format='json')
		self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)

	def test_seller_review_list_and_stats(self):
		# create multiple orders and reviews for same seller
		o2 = Order.objects.create(buyer=self.buyer, seller=self.seller, shipping_address='Addr2', total_price=200, status='CM')
		OrderItem.objects.create(order=o2, product=self.product, price=self.product.price, quantity=1)

		self.client.force_authenticate(user=self.buyer)
		self.client.post('/reviews', {'order_id': self.order.id, 'rating': 5}, format='json')
		self.client.post('/reviews', {'order_id': o2.id, 'rating': 3}, format='json')

		# List reviews
		r_list = self.client.get(f'/users/{self.seller.id}/reviews')
		self.assertEqual(r_list.status_code, status.HTTP_200_OK)
		self.assertEqual(len(r_list.data), 2)

		# Stats
		r_stats = self.client.get(f'/reviews/stats/{self.seller.id}')
		self.assertEqual(r_stats.status_code, status.HTTP_200_OK)
		self.assertEqual(r_stats.data['total_reviews'], 2)
		# avg of 5 and 3 = 4.0
		self.assertEqual(r_stats.data['avg_rating'], 4.0)
		self.assertEqual(r_stats.data['distribution'][5], 1)
		self.assertEqual(r_stats.data['distribution'][3], 1)

	def test_stats_no_reviews_returns_zeroes(self):
		# New seller with no reviews
		new_seller = User.objects.create_user(username='new', password='pass')
		r = self.client.get(f'/reviews/stats/{new_seller.id}')
		self.assertEqual(r.status_code, status.HTTP_200_OK)
		self.assertEqual(r.data['total_reviews'], 0)
		self.assertEqual(r.data['avg_rating'], 0)

