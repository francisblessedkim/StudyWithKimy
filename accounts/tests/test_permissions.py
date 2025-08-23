from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory
from accounts.models import User
from api.permissions import IsTeacher, IsAuthenticatedReadOnly
from django.contrib.auth.models import AnonymousUser  # Add this at the top


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.teacher = User.objects.create_user(
            username="teacher", role="teacher", password="pass"
        )
        self.student = User.objects.create_user(
            username="student", role="student", password="pass"
        )

    def test_is_teacher_permission(self):
        request = self.factory.get("/")
        request.user = self.teacher
        permission = IsTeacher()
        self.assertTrue(permission.has_permission(request, None))

        request.user = self.student
        self.assertFalse(permission.has_permission(request, None))

    def test_is_authenticated_read_only(self):
        request = self.factory.get("/")
        request.user = self.teacher
        permission = IsAuthenticatedReadOnly()
        self.assertTrue(permission.has_permission(request, None))

        post_request = self.factory.post("/")
        post_request.user = self.student
        self.assertFalse(permission.has_permission(post_request, None))

    def test_is_teacher_permission_unauthenticated(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        permission = IsTeacher()
        self.assertFalse(permission.has_permission(request, None))

    def test_is_authenticated_read_only_unauthenticated(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        permission = IsAuthenticatedReadOnly()
        self.assertFalse(permission.has_permission(request, None))

