# courses/views.py
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from social.models import Notification
from .forms import CourseForm, AssignmentForm, SubmissionForm
from .models import Course, Enrollment, Material, Feedback, Assignment, Submission


User = get_user_model()

def course_list(request):
    qs = Course.objects.select_related("teacher").order_by("title")
    return render(request, "courses/course_list.html", {"courses": qs})

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course.objects.select_related("teacher"), slug=slug)
    materials = Material.objects.filter(course=course).order_by("-created_at")
    enrolled = Enrollment.objects.filter(course=course, student=request.user,
                                         status=Enrollment.Status.ACTIVE).exists()
    enrollments = Enrollment.objects.select_related("student")\
                                   .filter(course=course).order_by("student__username")
    feedback_list = Feedback.objects.select_related("student")\
                                    .filter(course=course).order_by("-created_at")

    assignments = Assignment.objects.filter(course=course).order_by("due_date", "id")

    # Submissions
    submitted_ids = set()
    submissions_by_assignment = {}
    if getattr(request.user, "role", None) == "student":
        # used to show the “Submitted” badge
        submitted_ids = set(
            Submission.objects
            .filter(assignment__course=course, student=request.user)
            .values_list("assignment_id", flat=True)
        )
    elif getattr(request.user, "role", None) == "teacher" and course.teacher_id == request.user.id:
        # teacher view: group submissions by assignment
        for a in assignments:
            submissions_by_assignment[a.id] = list(
                Submission.objects
                .select_related("student")
                .filter(assignment=a)
                .order_by("-submitted_at")
            )

    # Collect all submissions for this course (teacher view)
    all_subs = (
        Submission.objects
        .select_related("student", "assignment")
        .filter(assignment__course=course)
    )

    subs_by_assignment: dict[int, list[Submission]] = {}
    for s in all_subs:
        subs_by_assignment.setdefault(s.assignment_id, []).append(s)

    # Build rows: (assignment, matching submissions)
    assignment_rows = [
        {"a": a, "subs": subs_by_assignment.get(a.id, [])}
        for a in assignments
    ]

    context = {
        "course": course,
        "materials": materials,
        "enrolled": enrolled,
        "enrollments": enrollments,
        "feedback_list": feedback_list,
        "assignments": assignments,
        "submitted_ids": submitted_ids,  
        "submissions_by_assignment": submissions_by_assignment,
        "assignment_rows": assignment_rows,
    }
    return render(request, "courses/course_detail.html", context)

@login_required
@require_POST
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if getattr(request.user, "role", None) != "student":
        raise PermissionDenied("Only students can enroll.")
    Enrollment.objects.get_or_create(
        course=course,
        student=request.user,
        defaults={"status": Enrollment.Status.ACTIVE},
    )
    messages.success(request, f"Enrolled in {course.title}.")
    return redirect("course_detail", slug=slug)

@login_required
@require_POST
def unenroll(request, slug):
    course = get_object_or_404(Course, slug=slug)
    Enrollment.objects.filter(course=course, student=request.user).delete()
    messages.success(request, f"Unenrolled from {course.title}.")
    return redirect("course_detail", slug=slug)


@login_required
@require_POST
def teacher_remove_student(request, slug, username):
    course = get_object_or_404(Course, slug=slug)
    if course.teacher_id != request.user.id:
        raise PermissionDenied("Only the course teacher can remove students.")
    student = get_object_or_404(User, username=username)
    Enrollment.objects.filter(course=course, student=student).delete()

    Notification.objects.create(
        recipient=student,
        type=Notification.Type.REMOVED,
        payload={
            "course_id": course.id,
            "course_title": course.title,
            "teacher_username": request.user.username,
        },
    )

    messages.success(request, f"Removed @{student.username} from {course.title}.")
    return redirect("course_detail", slug=slug)

@login_required
def material_add(request, slug):
    # simple HTML form to upload material (your template already links here)
    course = get_object_or_404(Course, slug=slug)
    if course.teacher_id != request.user.id:
        raise PermissionDenied("Only the course teacher can upload materials.")
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        f = request.FILES.get("file")
        if not f:
            messages.error(request, "Please choose a file.")
        else:
            Material.objects.create(course=course, title=title or f.name, file=f)
            messages.success(request, "Material uploaded.")
            return redirect("course_detail", slug=slug)
    return render(request, "courses/material_form.html", {"course": course})

@login_required
@require_POST
def feedback_submit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if getattr(request.user, "role", None) != "student":
        raise PermissionDenied("Only students can leave feedback.")
    rating_raw = request.POST.get("rating")
    try:
        rating = int(rating_raw)
    except (TypeError, ValueError):
        rating = 0
    comment = (request.POST.get("comment") or "").strip()
    if not (1 <= rating <= 5):
        messages.error(request, "Rating must be between 1 and 5.")
        return redirect("course_detail", slug=slug)
    Feedback.objects.update_or_create(
        course=course, student=request.user,
        defaults={"rating": rating, "comment": comment},
    )
    messages.success(request, "Feedback submitted.")
    return redirect("course_detail", slug=slug)

@login_required
def course_create(request):
    if getattr(request.user, "role", None) != "teacher":
        raise PermissionDenied("Only teachers can create courses.")
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, "Course created.")
            return redirect("course_detail", slug=course.slug)
    else:
        form = CourseForm()
    return render(request, "courses/course_form.html", {"form": form})

@login_required
@require_POST
def teacher_block_student(request, slug, username):
    course = get_object_or_404(Course, slug=slug)
    if course.teacher_id != request.user.id:
        raise PermissionDenied()
    student = get_object_or_404(User, username=username)
    Enrollment.objects.filter(course=course, student=student).update(status=Enrollment.Status.BLOCKED)
    # Optional notification if you add types:
    # Notification.objects.create(recipient=student, type=Notification.Type.BLOCKED, payload={...})
    messages.success(request, f"Blocked @{student.username}.")
    return redirect("course_detail", slug=slug)

@login_required
@require_POST
def teacher_unblock_student(request, slug, username):
    course = get_object_or_404(Course, slug=slug)
    if course.teacher_id != request.user.id:
        raise PermissionDenied()
    student = get_object_or_404(User, username=username)
    Enrollment.objects.filter(course=course, student=student).update(status=Enrollment.Status.ACTIVE)
    # Optional notification:
    # Notification.objects.create(recipient=student, type=Notification.Type.UNBLOCKED, payload={...})
    messages.success(request, f"Unblocked @{student.username}.")
    return redirect("course_detail", slug=slug)


@login_required
def assignment_create(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if course.teacher_id != request.user.id:
        raise PermissionDenied("Only the course teacher can create assignments.")
    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            a = form.save(commit=False)
            a.course = course
            a.save()
            messages.success(request, "Assignment created.")
            return redirect("course_detail", slug=slug)
    else:
        form = AssignmentForm()
    return render(request, "courses/assignment_form.html", {"course": course, "form": form})

@login_required
def submission_create(request, slug, assignment_id):
    course = get_object_or_404(Course, slug=slug)
    assignment = get_object_or_404(Assignment, pk=assignment_id, course=course)
    # must be enrolled and a student
    if getattr(request.user, "role", None) != "student":
        raise PermissionDenied("Only students can submit.")
    if not Enrollment.objects.filter(course=course, student=request.user, status=Enrollment.Status.ACTIVE).exists():
        raise PermissionDenied("You are not enrolled on this course.")
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub, created = Submission.objects.update_or_create(
                assignment=assignment, student=request.user,
                defaults={"file": form.cleaned_data.get("file"), "text": form.cleaned_data.get("text")},
            )
            messages.success(request, "Submission saved.")
            return redirect("course_detail", slug=slug)
    else:
        form = SubmissionForm()
    return render(request, "courses/submission_form.html", {"course": course, "assignment": assignment, "form": form})