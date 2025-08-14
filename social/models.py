from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class StatusUpdate(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="status_updates")
    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.author}: {self.text[:40]}"

class Notification(models.Model):
    class Type(models.TextChoices):
        ENROLMENT = "enrolment", "New enrolment"
        NEW_MATERIAL = "new_material", "New material"

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=20, choices=Type.choices)
    payload = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.type} → {self.recipient}"
