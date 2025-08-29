# accounts/tests/test_dashboard.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardAccessTests(TestCase):
    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse("dashboard"))
        self.assertIn(resp.status_code, (302, 301))

    def test_dashboard_ok_when_logged_in(self):
        u = User.objects.create_user(username="kim", password="pass123", role="student")
        self.client.login(username="kim", password="pass123")
        resp = self.client.get(reverse("dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Welcome back")
