from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user( # type: ignore
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
            role="student",
            display_name="Test User",
            bio="Hello, I am a test user."
        )
        print(dir(user))
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.role, "student") # type: ignore
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        admin = User.objects.create_superuser( # type: ignore
            username="adminuser",
            email="admin@example.com",
            password="adminpass"
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_user_str_representation(self):
        user = User.objects.create_user( # type: ignore
        username="testuser2",
        email="test2@example.com",
        password="pass12345",
        display_name="Tester Name",
        )
        self.assertEqual(str(user), "Tester Name")  # Adjust this if your __str__ returns something else



