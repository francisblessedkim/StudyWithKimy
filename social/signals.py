# social/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification
from courses.models import Enrollment, Material

User = get_user_model()

@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrolment(sender, instance: Enrollment, created, **kwargs):
    if not created:
        return
    course = instance.course
    teacher = getattr(course, "teacher", None)
    if not teacher:
        return
    Notification.objects.create(
        recipient=teacher,
        type=Notification.Type.ENROLMENT,
        payload={
            "course_id": course.id,
            "course_title": getattr(course, "title", ""),
            "student_username": getattr(instance.student, "username", ""),
        },
    )

@receiver(post_save, sender=Material)
def notify_students_on_new_material(sender, instance: Material, created, **kwargs):
    if not created:
        return
    course = instance.course
    # all active enrollments; adjust if your Enrollment has a different status field/value
    enrollments = course.enrollments.select_related("student").all()
    for enr in enrollments:
        student = enr.student
        Notification.objects.create(
            recipient=student,
            type=Notification.Type.NEW_MATERIAL,
            payload={
                "course_id": course.pk,
                "course_title": getattr(course, "title", ""),
                "material_id": instance.pk,
                "material_title": getattr(instance, "title", "") or getattr(instance.file, "name", ""),
            },
        )
