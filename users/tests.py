from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class UsersTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='tester', email='t@example.com', password='pass')

	def test_me_requires_authentication(self):
		resp = self.client.get('/api/me/')
		self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

	def test_get_me_returns_profile_fields(self):
		self.client.force_authenticate(user=self.user)
		resp = self.client.get('/api/me/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['username'], self.user.username)
		self.assertIn('address', resp.data)
		self.assertIn('rating', resp.data)
		self.assertIn('num_reviews', resp.data)

	def test_patch_updates_address(self):
		self.client.force_authenticate(user=self.user)
		resp = self.client.patch('/api/me/', {'address': 'New Address'}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(resp.data['address'], 'New Address')

	def test_patch_unknown_field_ignored(self):
		self.client.force_authenticate(user=self.user)
		original_rating = self.user.profile.rating 
		resp = self.client.patch('/api/me/', {'rating': 5}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.user.profile.refresh_from_db() # Load lại từ DB
		self.assertEqual(self.user.profile.rating, original_rating) # Phải vẫn là 0, không được là 5

