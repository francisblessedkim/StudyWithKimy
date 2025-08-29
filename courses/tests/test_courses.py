# courses/tests/test_courses.py
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment, Material, Feedback

User = get_user_model()

@override_settings(MEDIA_ROOT="/tmp/test_media")
class CourseHtmlFlowsTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="t1", password="pass123", role="teacher"
        )
        self.student = User.objects.create_user(
            username="s1", password="pass123", role="student"
        )
        self.course = Course.objects.create(
            title="AI Engineering",
            description="Intro",
            teacher=self.teacher,
        )

    def test_course_list_renders(self):
        resp = self.client.get(reverse("course_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Browse Courses")
        self.assertContains(resp, "AI Engineering")

    def test_course_detail_requires_login(self):
        url = reverse("course_detail", args=[self.course.slug])
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (302, 301))  # redirect to login

    def test_student_enroll_and_unenroll(self):
        self.client.login(username="s1", password="pass123")
        enroll_url = reverse("course_enroll", args=[self.course.slug])
        resp = self.client.post(enroll_url)
        self.assertRedirects(resp, reverse("course_detail", args=[self.course.slug]))
        self.assertTrue(
            Enrollment.objects.filter(course=self.course, student=self.student, status="active").exists()
        )

        unenroll_url = reverse("course_unenroll", args=[self.course.slug])
        resp2 = self.client.post(unenroll_url)
        self.assertRedirects(resp2, reverse("course_detail", args=[self.course.slug]))
        self.assertFalse(
            Enrollment.objects.filter(course=self.course, student=self.student).exists()
        )

    def test_teacher_upload_material_via_html_form(self):
        self.client.login(username="t1", password="pass123")
        url = reverse("material_add", args=[self.course.slug])
        fake = SimpleUploadedFile("notes.txt", b"hello", content_type="text/plain")
        resp = self.client.post(url, {"title": "Week 1", "file": fake})
        self.assertRedirects(resp, reverse("course_detail", args=[self.course.slug]))
        self.assertTrue(Material.objects.filter(course=self.course, title="Week 1").exists())

    def test_student_feedback_submit(self):
        self.client.login(username="s1", password="pass123")
        Enrollment.objects.create(course=self.course, student=self.student, status=Enrollment.Status.ACTIVE)
        url = reverse("feedback_submit", args=[self.course.slug])
        resp = self.client.post(url, {"rating": "5", "comment": "Great!"})
        self.assertRedirects(resp, reverse("course_detail", args=[self.course.slug]))
        fb = Feedback.objects.get(course=self.course, student=self.student)
        self.assertEqual(fb.rating, 5)
        self.assertEqual(fb.comment, "Great!")
