from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from accounts.models import User
from courses.models import Course

class CourseAPITest(APITestCase):
    def setUp(self):
        self.client: APIClient = APIClient()
        self.teacher = User.objects.create_user(
            username="teacher",
            password="testpass123",
            role="teacher"
        )
        self.student = User.objects.create_user(
            username="student",
            password="testpass123",
            role="student"
        )
        self.url = reverse("courses-list")


    def test_teacher_can_create_course(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            "title": "Django Basics",
            "description": "Learn Django",
            "start_date": "2025-09-01",
            "end_date": "2025-12-01",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 201) # type: ignore
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.first().teacher, self.teacher) # type: ignore

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.url, {
            "title": "Hack Django"
        }, format="json")
        self.assertEqual(response.status_code, 403) # type: ignore

    def test_unauthenticated_user_cannot_view_courses(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403) # type: ignore

    def test_teacher_can_view_their_courses(self):
        Course.objects.create(title="Django", teacher=self.teacher)
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) # type: ignore
        self.assertEqual(len(response.data["results"]), 1) # type: ignore
