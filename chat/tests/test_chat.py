# chat/tests/test_chat.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from chat.models import ChatMessage

User = get_user_model()

class ChatHistoryTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass123", role="student")
        self.u2 = User.objects.create_user(username="u2", password="pass123", role="teacher")
        ChatMessage.objects.create(sender=self.u1, receiver=self.u2, message="hi")
        ChatMessage.objects.create(sender=self.u2, receiver=self.u1, message="hello")

    def test_history_endpoint_returns_messages(self):
        self.client.login(username="u1", password="pass123")
        url = reverse("chat:chat_history", args=[self.u2.username])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("messages", data)
        self.assertEqual(len(data["messages"]), 2)
        self.assertEqual(data["messages"][0]["message"], "hi")
