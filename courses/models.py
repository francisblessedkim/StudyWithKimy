from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courses",
        limit_choices_to={"role": "teacher"}
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "course"
            slug = base
            i = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DROPPED = "dropped", "Dropped"
        BLOCKED = "blocked", "Blocked"

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments",
        limit_choices_to={"role": "student"}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} → {self.course} ({self.status})"

class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="materials/%Y/%m/%d")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.course})"

class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="feedback")
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="feedback",
        limit_choices_to={"role": "student"}
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "student")

    def __str__(self):
        return f"{self.course} ← {self.student} [{self.rating}]"
