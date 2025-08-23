from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"

    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.STUDENT)
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # def __str__(self):
    #     return self.username
    def __str__(self):
        return self.display_name or self.username
