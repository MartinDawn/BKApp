from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Product, Category


class StoreTests(APITestCase):
	def setUp(self):
		self.seller1 = User.objects.create_user(username='seller1', password='pass')
		self.seller2 = User.objects.create_user(username='seller2', password='pass')

		self.cat = Category.objects.create(name='Books')

		# Products
		self.p1 = Product.objects.create(seller=self.seller1, category=self.cat, title='Book A', price=100)
		self.p2 = Product.objects.create(seller=self.seller2, category=self.cat, title='Book B', price=200)

	def test_category_list(self):
		resp = self.client.get('/categories/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertTrue(any(c['id'] == self.cat.id for c in resp.data))

	def test_product_list_anonymous(self):
		resp = self.client.get('/products/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		# At least two products
		self.assertGreaterEqual(len(resp.data['results']), 2)

	def test_create_product_requires_auth_and_sets_seller(self):
		payload = {'title': 'New Book', 'price': 50, 'category': self.cat.id, 'condition': 'NE'}

		# Anonymous -> should be 401
		r = self.client.post('/products/', payload, format='json')
		self.assertIn(r.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

		# Authenticated -> create
		self.client.force_authenticate(user=self.seller1)
		r2 = self.client.post('/products/', payload, format='json')
		if r2.status_code != status.HTTP_201_CREATED:
			print("Lỗi API trả về:", r2.data)
		self.assertEqual(r2.status_code, status.HTTP_201_CREATED)
		self.assertEqual(r2.data['seller'], self.seller1.id)
		# condition_display should be present
		self.assertIn('condition_display', r2.data)

	def test_update_and_delete_permissions(self):
		# seller1 can update own product
		self.client.force_authenticate(user=self.seller1)
		r = self.client.patch(f'/products/{self.p1.id}/', {'title': 'Book A Updated'}, format='json')
		self.assertEqual(r.status_code, status.HTTP_200_OK)
		self.p1.refresh_from_db()
		self.assertEqual(self.p1.title, 'Book A Updated')

		# other user cannot update
		self.client.force_authenticate(user=self.seller2)
		r2 = self.client.patch(f'/products/{self.p1.id}/', {'title': 'Hacked'}, format='json')
		self.assertEqual(r2.status_code, status.HTTP_403_FORBIDDEN)

		# owner can delete
		self.client.force_authenticate(user=self.seller1)
		rdel = self.client.delete(f'/products/{self.p1.id}/')
		self.assertEqual(rdel.status_code, status.HTTP_204_NO_CONTENT)

