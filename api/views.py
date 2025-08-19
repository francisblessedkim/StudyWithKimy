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

# ----- Courses -----
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("teacher").all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsTeacher()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # Teacher creating their own course
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
# class MaterialViewSet(mixins.CreateModelMixin,
#                       mixins.ListModelMixin,
#                       mixins.DestroyModelMixin,
#                       viewsets.GenericViewSet):
#     serializer_class = MaterialSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]  # <-- add this line

#     def get_queryset(self):
#         qs = Material.objects.select_related("course", "course__teacher")
#         user = self.request.user
#         if getattr(user, "role", None) == "teacher":
#             return qs.filter(course__teacher=user)
#         return qs.filter(course__enrollments__student=user, course__enrollments__status="active")

#     def get_permissions(self):
#         if self.action in ["create", "destroy"]:
#             return [IsTeacher()]
#         return super().get_permissions()

#     @extend_schema(
#         request={"multipart/form-data": MaterialSerializer},   # <-- force file upload UI
#         responses=MaterialSerializer,
# )
#     def create(self, request, *args, **kwargs):
#         return super().create(request, *args, **kwargs)

@extend_schema_view(
    create=extend_schema(
        request={"multipart/form-data": MaterialSerializer},  # force file upload UI
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

    # def get_queryset(self):
    #     qs = Material.objects.select_related("course", "course__teacher")
    #     user = self.request.user
    #     if getattr(user, "role", None) == "teacher":
    #         return qs.filter(course__teacher=user)
    #     return qs.filter(course__enrollments__student=user, course__enrollments__status="active")

    # def get_permissions(self):
    #     if self.action in ["create", "destroy"]:
    #         return [IsTeacher()]
    #     return super().get_permissions()

    def get_queryset(self):
        qs = Material.objects.select_related("course", "course__teacher")
        user = self.request.user
        if getattr(user, "role", None) == "teacher":
            qs = qs.filter(course__teacher=user)
        else:
            qs = qs.filter(course__enrollments__student=user,
                           course__enrollments__status="active")

        # NEW: support ?course=<id>
        req = cast(Request, self.request)
        course_id = req.query_params.get("course")
        if course_id:
            qs = qs.filter(course_id=course_id)

        return qs.order_by("-created_at")




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
