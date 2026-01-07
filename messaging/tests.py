from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import Conversation, Message
from store.models import Product


class MessagingTests(APITestCase):
	def setUp(self):
		# Users
		self.u1 = User.objects.create_user(username='alice', password='pass')
		self.u2 = User.objects.create_user(username='bob', password='pass')
		# Product (optional attach to messages)
		self.product = Product.objects.create(seller=self.u2, title='Test Product', price=100)

		# Conversation between alice and bob
		self.chat = Conversation.objects.create(participant1=self.u1, participant2=self.u2)

	def test_chat_list_includes_conversation(self):
		self.client.force_authenticate(user=self.u1)
		resp = self.client.get('/chats')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		# Should have at least one conversation
		self.assertIsInstance(resp.data, list)
		self.assertTrue(any(c['id'] == self.chat.id for c in resp.data))

	def test_message_list_and_creation(self):
		# create some messages
		m1 = Message.objects.create(conversation=self.chat, sender=self.u1, content='Hello')
		m2 = Message.objects.create(conversation=self.chat, sender=self.u2, content='Hi there')

		self.client.force_authenticate(user=self.u1)
		# GET messages
		resp = self.client.get(f'/chats/{self.chat.id}/messages')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(len(resp.data), 2)
		self.assertEqual(resp.data[0]['content'], 'Hello')

		# POST a new message with product_id
		payload = {'content': 'Is this available?', 'product_id': self.product.id}
		post_resp = self.client.post(f'/chats/{self.chat.id}/messages', payload, format='json')
		
		if post_resp.status_code != 201:
			print("Lỗi API trả về:", post_resp.data)

		self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(post_resp.data['content'], 'Is this available?')
		# product should be nested in response
		self.assertIsNotNone(post_resp.data.get('product'))
		self.assertEqual(post_resp.data['product']['id'], self.product.id)

	def test_mark_read_updates_messages(self):
		# message from bob unread
		msg = Message.objects.create(conversation=self.chat, sender=self.u2, content='Please reply', is_read=False)

		self.client.force_authenticate(user=self.u1)
		resp = self.client.post(f'/chats/{self.chat.id}/read')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)

		msg.refresh_from_db()
		self.assertTrue(msg.is_read)

	def test_start_chat_creates_and_returns_existing(self):
		# create a new user to start chat with
		u3 = User.objects.create_user(username='charlie', password='pass')

		self.client.force_authenticate(user=self.u1)
		# start new chat
		resp_new = self.client.post('/chats/start', {'target_user_id': u3.id}, format='json')
		self.assertIn(resp_new.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))
		self.assertIn('chat_id', resp_new.data)

		# start chat with existing participant (bob)
		resp_exist = self.client.post('/chats/start', {'target_user_id': self.u2.id}, format='json')
		self.assertEqual(resp_exist.status_code, status.HTTP_200_OK)
		self.assertIn('chat_id', resp_exist.data)

