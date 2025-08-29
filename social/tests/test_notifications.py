# social/tests/test_notifications.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment, Material
from social.models import Notification

User = get_user_model()

class NotificationApiTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teach", password="x", role="teacher")
        self.student = User.objects.create_user(username="stud", password="x", role="student")
        self.course = Course.objects.create(title="ML 101", description="desc", teacher=self.teacher)

    def test_mark_all_read(self):
        # create two notifications for the student
        Notification.objects.create(recipient=self.student, type=Notification.Type.ENROLMENT, payload={})
        Notification.objects.create(recipient=self.student, type=Notification.Type.NEW_MATERIAL, payload={})

        self.client.login(username="stud", password="x")
        url = reverse("notification-list")  # router basename: notifications
        # sanity: list
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # mark all read
        mark_url = reverse("notification-mark-all-read")
        resp2 = self.client.post(mark_url)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(Notification.objects.filter(recipient=self.student, is_read=False).count(), 0)

    def test_signal_on_enrolment_creates_teacher_notification(self):
        # student enrolls (your HTML path uses POST to /courses/<slug>/enrol/)
        self.client.login(username="stud", password="x")
        enrol_url = reverse("course_enrol_alias", args=[self.course.slug])  # supports both spellings
        resp = self.client.post(enrol_url)
        self.assertIn(resp.status_code, (302, 301))

        # expect a notification for teacher OR student (depending on your signals)
        # most setups notify teacher when a student enrolls:
        qs = Notification.objects.filter(recipient=self.teacher, type=Notification.Type.ENROLMENT)
        self.assertTrue(qs.exists(), "Expected ENROLMENT notification for teacher")

    def test_signal_on_material_upload_notifies_enrolled_students(self):
        # enroll student first
        Enrollment.objects.create(course=self.course, student=self.student, status=Enrollment.Status.ACTIVE)

        # upload material as teacher (simulate via model create—your signal should fire on post_save)
        Material.objects.create(course=self.course, title="Week 1", file="materials/test.txt")

        # expect NEW_MATERIAL notification for the enrolled student
        qs = Notification.objects.filter(recipient=self.student, type=Notification.Type.NEW_MATERIAL)
        self.assertTrue(qs.exists(), "Expected NEW_MATERIAL notification for enrolled student(s)")
