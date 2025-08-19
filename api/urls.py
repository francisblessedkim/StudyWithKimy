from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MeViewSet, PublicUserViewSet,
    CourseViewSet, EnrollmentViewSet, MaterialViewSet, FeedbackViewSet,
    StatusUpdateViewSet, NotificationViewSet
)

router = DefaultRouter()
router.register(r"me", MeViewSet, basename="me")
router.register(r"users", PublicUserViewSet, basename="users")
router.register(r"courses", CourseViewSet, basename="courses")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")
router.register(r"materials", MaterialViewSet, basename="materials")
router.register(r"feedback", FeedbackViewSet, basename="feedback")
router.register(r"status-updates", StatusUpdateViewSet, basename="status-updates")
router.register(r"notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("", include(router.urls)),
]
