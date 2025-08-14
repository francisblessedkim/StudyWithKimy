from django.contrib import admin
from .models import Course, Enrollment, Material, Feedback

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "start_date", "end_date", "created_at")
    search_fields = ("title", "description", "teacher__username")
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "status", "created_at")
    list_filter = ("status", "course")

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "created_at")
    search_fields = ("title", "course__title")

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("course", "student", "rating", "created_at")
    list_filter = ("rating", "course")
