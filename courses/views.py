from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Course, Enrollment, Material

def course_list(request):
    qs = Course.objects.select_related("teacher").order_by("title")
    return render(request, "courses/course_list.html", {"courses": qs})

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course.objects.select_related("teacher"), slug=slug)
    materials = Material.objects.filter(course=course).order_by("-created_at")
    is_enrolled = Enrollment.objects.filter(course=course, student=request.user, status="active").exists()
    can_enroll = (getattr(request.user, "role", None) == "student") and not is_enrolled
    return render(request, "courses/course_detail.html", {
        "course": course, "materials": materials,
        "is_enrolled": is_enrolled, "can_enroll": can_enroll
    })

@login_required
@require_POST
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if getattr(request.user, "role", None) == "student":
        Enrollment.objects.get_or_create(course=course, student=request.user, defaults={"status": "active"})
    return redirect("course_detail", slug=slug)
