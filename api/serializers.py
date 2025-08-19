from rest_framework import serializers
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment, Material, Feedback
from social.models import StatusUpdate, Notification

User = get_user_model()

# --- Users ---
class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "display_name", "bio"]

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "display_name", "bio", "role"]

# --- Courses ---

class CourseSerializer(serializers.ModelSerializer):
    teacher = PublicUserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "description",
            "start_date", "end_date",
            "teacher", "created_at"
        ]
        read_only_fields = ["id", "slug", "created_at", "teacher"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student = PublicUserSerializer(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "status", "created_at"]
        read_only_fields = ["id", "student", "status", "created_at"]

class MaterialSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=True)  # <-- explicit, so Spectacular flags it as binary

    class Meta:
        model = Material
        fields = ["id", "course", "title", "file", "created_at"]
        read_only_fields = ["id", "created_at"]

class FeedbackSerializer(serializers.ModelSerializer):
    student = PublicUserSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = ["id", "course", "student", "rating", "comment", "created_at"]
        read_only_fields = ["id", "student", "created_at"]

# --- Social ---
class StatusUpdateSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(read_only=True)

    class Meta:
        model = StatusUpdate
        fields = ["id", "author", "text", "created_at"]
        read_only_fields = ["id", "author", "created_at"]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "type", "payload", "is_read", "created_at"]
        read_only_fields = ["id", "type", "payload", "created_at"]
