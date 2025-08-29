# api/tests/test_api.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from courses.models import Course, Enrollment

User = get_user_model()

class ApiEndpointsTests(APITestCase):
    def setUp(self):
        self.client: APIClient = APIClient()
        self.teacher = User.objects.create_user(username="teach", password="pass123", role="teacher")
        self.student = User.objects.create_user(username="stud",  password="pass123", role="student")
        self.courses_url = reverse("courses-list")           # router basename: "courses"
        self.materials_url = reverse("materials-list")       # "materials"
        self.enrollments_url = reverse("enrollments-list")   # "enrollments"

        self.course = Course.objects.create(title="Data Science", description="ds", teacher=self.teacher)

    def test_courses_list_requires_auth(self):
        resp = self.client.get(self.courses_url)
        self.assertEqual(resp.status_code, 403)

    def test_teacher_can_create_course_via_api(self):
        self.client.force_authenticate(user=self.teacher)
        resp = self.client.post(self.courses_url, {"title": "New API Course", "description": "x"}, format="json")
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["teacher"]["username"], "teach")

    def test_student_cannot_create_course_via_api(self):
        self.client.force_authenticate(user=self.student)
        resp = self.client.post(self.courses_url, {"title": "Nope", "description": "x"}, format="json")
        self.assertIn(resp.status_code, (401, 403))

    def test_enrollments_visibility(self):
        Enrollment.objects.create(course=self.course, student=self.student, status=Enrollment.Status.ACTIVE)

        self.client.force_authenticate(user=self.student)
        resp_student = self.client.get(self.enrollments_url)
        self.assertEqual(resp_student.status_code, 200)
        # pagination or not: normalize
        data_student = resp_student.data["results"] if isinstance(resp_student.data, dict) and "results" in resp_student.data else resp_student.data
        self.assertEqual(len(data_student), 1)

        self.client.force_authenticate(user=self.teacher)
        resp_teacher = self.client.get(self.enrollments_url)
        self.assertEqual(resp_teacher.status_code, 200)
        data_teacher = resp_teacher.data["results"] if isinstance(resp_teacher.data, dict) and "results" in resp_teacher.data else resp_teacher.data
        self.assertEqual(len(data_teacher), 1)

    def test_teacher_uploads_material_and_filter_by_course(self):
        self.client.force_authenticate(user=self.teacher)
        f = SimpleUploadedFile("week1.txt", b"hello", content_type="text/plain")
        resp = self.client.post(self.materials_url, {"course": self.course.id, "title": "Week1", "file": f}, format="multipart")
        self.assertEqual(resp.status_code, 201, resp.data)

        # filter by course
        resp2 = self.client.get(self.materials_url, {"course": str(self.course.id)})
        self.assertEqual(resp2.status_code, 200)
        data = resp2.data["results"] if isinstance(resp2.data, dict) and "results" in resp2.data else resp2.data
        self.assertGreaterEqual(len(data), 1)
