from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Enrollment, Material
from social.models import Notification

@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrollment(sender, instance: Enrollment, created, **kwargs):
    if not created or instance.status != Enrollment.Status.ACTIVE:
        return
    teacher = instance.course.teacher
    def _create():
        Notification.objects.create(
            recipient=teacher,
            type=Notification.Type.ENROLMENT,
            payload={
                "course": instance.course.title,
                "course_slug": instance.course.slug,
                "student": instance.student.username,
            },
        )
    transaction.on_commit(_create)

@receiver(post_save, sender=Material)
def notify_students_on_new_material(sender, instance: Material, created, **kwargs):
    if not created:
        return
    course = instance.course
    def _bulk():
        to_create = []
        qs = course.enrollments.filter(status="active").select_related("student")  # type: ignore
        for enr in qs:
            to_create.append(Notification(
                recipient=enr.student,
                type=Notification.Type.NEW_MATERIAL,
                payload={
                    "course": course.title,
                    "course_slug": course.slug,
                    "material_title": instance.title,
                    "material_id": instance.id,  # type: ignore
                },
            ))
        if to_create:
            Notification.objects.bulk_create(to_create)
    transaction.on_commit(_bulk)

