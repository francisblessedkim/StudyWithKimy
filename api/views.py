from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.request import Request
from typing import cast
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema_view, extend_schema
from typing import cast
from courses.models import Course
from api.serializers import CourseSerializer
from api.permissions import IsTeacher




from .permissions import IsTeacher, IsOwnerOrReadOnly, IsAuthenticatedReadOnly
from .serializers import (
    PublicUserSerializer, MeSerializer,
    CourseSerializer, EnrollmentSerializer, MaterialSerializer, FeedbackSerializer,
    StatusUpdateSerializer, NotificationSerializer
)
from courses.models import Course, Enrollment, Material, Feedback
from social.models import StatusUpdate, Notification

User = get_user_model()

# ----- Users -----
class MeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        return Response(MeSerializer(request.user).data)

class PublicUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    lookup_field = "username"
    permission_classes = [permissions.IsAuthenticated]  # profiles are visible to logged-in users


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    # def get_queryset(self):
    #     user = self.request.user
    #     if getattr(user, "role", None) == "teacher":
    #         return Course.objects.filter(teacher=user).order_by("id")
    #     return Course.objects.none()  # block access for students/others if needed

    # api/views.py  (inside CourseViewSet)
    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "teacher":
            return Course.objects.filter(teacher=user).order_by("id")
        # let students see available courses via the API
        return Course.objects.all().order_by("id")


    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsTeacher()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Automatically assign the authenticated teacher as the course creator
        serializer.save(teacher=self.request.user)

# ----- Enrollments -----
class EnrollmentViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Teachers see enrollments on their courses; students see their own enrollments
        if getattr(user, "role", None) == "teacher":
            return Enrollment.objects.select_related("student", "course").filter(course__teacher=user)
        return Enrollment.objects.select_related("student", "course").filter(student=user)

    def perform_create(self, serializer):
        # Student self-enrols
        serializer.save(student=self.request.user, status=Enrollment.Status.ACTIVE)

# ----- Materials -----

# @extend_schema_view(
#     create=extend_schema(
#         request={"multipart/form-data": MaterialSerializer},  # force file upload UI
#         responses=MaterialSerializer,
#     )
# )
# class MaterialViewSet(mixins.CreateModelMixin,
#                       mixins.ListModelMixin,
#                       mixins.DestroyModelMixin,
#                       viewsets.GenericViewSet):
#     serializer_class = MaterialSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]

#     def get_queryset(self):
#         qs = Material.objects.select_related("course", "course__teacher")
#         user = self.request.user
#         if getattr(user, "role", None) == "teacher":
#             qs = qs.filter(course__teacher=user)
#         else:
#             qs = qs.filter(course__enrollments__student=user,
#                            course__enrollments__status="active")

#         # NEW: support ?course=<id>
#         req = cast(Request, self.request)
#         course_id = req.query_params.get("course")
#         if course_id:
#             qs = qs.filter(course_id=course_id)

#         return qs.order_by("-created_at")


# ----- Materials -----
@extend_schema_view(
    create=extend_schema(
        request={"multipart/form-data": MaterialSerializer},  # keep this
        responses=MaterialSerializer,
    )
)
class MaterialViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        # Teachers only for create/destroy; anyone logged in may list their accessible materials
        if self.action in ["create", "destroy"]:
            return [IsTeacher()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Material.objects.select_related("course", "course__teacher")
        user = self.request.user
        if getattr(user, "role", None) == "teacher":
            qs = qs.filter(course__teacher=user)
        else:
            qs = qs.filter(course__enrollments__student=user,
                           course__enrollments__status="active")

        course_id = self.request.query_params.get("course")
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        # Only the owning teacher may upload
        if getattr(self.request.user, "role", None) != "teacher" or course.teacher_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the owning teacher can upload materials for this course.")
        serializer.save()




# ----- Feedback -----
class FeedbackViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Public read on course page later; API requires auth
        qs = Feedback.objects.select_related("course", "student")
        req = cast(Request, self.request)
        course_id = req.query_params.get("course")
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

# ----- Status Updates -----
class StatusUpdateViewSet(viewsets.ModelViewSet):
    serializer_class = StatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = StatusUpdate.objects.select_related("author")
        req = cast(Request, self.request)
        user = req.query_params.get("user")
        if user:
            qs = qs.filter(author__username=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# ----- Notifications -----
class NotificationViewSet(mixins.ListModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        qs = self.get_queryset().filter(is_read=False)
        updated = qs.update(is_read=True)
        return Response({"updated": updated})
