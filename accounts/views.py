from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import OuterRef, Subquery, Q
from django.utils.timezone import now, timedelta


from courses.models import Course, Enrollment, Material, Assignment
from social.models import StatusUpdate, Notification
from accounts.forms import SignupForm

User = get_user_model()

def signup(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! 🎉")
            return redirect('/dashboard/')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})



def landing_page(request):
        return render(request, "landing.html")

@login_required
def dashboard(request):
    me = request.user
    my_courses_taught = Course.objects.filter(teacher=me) if getattr(me, "role", None) == "teacher" else []
    my_enrollments = Enrollment.objects.select_related("course").filter(student=me, status="active")
    my_materials = Material.objects.filter(course__teacher=me)[:10] if getattr(me, "role", None) == "teacher" else []
    notifications = Notification.objects.filter(recipient=me, is_read=False)[:10]
    users = User.objects.exclude(id=me.id) 
    
    # my_updates = StatusUpdate.objects.filter(author=me)[:20]
    my_updates = StatusUpdate.objects.filter(author=me).order_by("-created_at")[:20]
    
    # Add this line to get all users except the current one
    users = User.objects.exclude(id=me.id)

    # upcoming deadlines 
    upcoming_assignments = []
    if getattr(me, "role", None) == "student":
        upcoming_assignments = (
            Assignment.objects.filter(
                course__enrollments__student=me,
                course__enrollments__status="active",
                due_date__isnull=False,
                due_date__gte=now(),
            ).order_by("due_date")[:5]
        )
    elif getattr(me, "role", None) == "teacher":
        upcoming_assignments = (
            Assignment.objects.filter(
                course__teacher=me,
                due_date__isnull=False,
                due_date__gte=now(),
            ).order_by("due_date")[:5]
        )

    return render(request, "accounts/dashboard.html", {
        "my_courses_taught": my_courses_taught,
        "my_enrollments": my_enrollments,
        "my_materials": my_materials,
        "notifications": notifications,
        "users": users, 
        "my_updates": my_updates,
        "upcoming_assignments": upcoming_assignments,
    })

def public_profile(request, username):
    profile = get_object_or_404(User, username=username)

    # Recent public status updates by this user
    statuses = (
        StatusUpdate.objects
        .filter(author=profile)
        .order_by("-created_at")[:10]
    )

    # Courses they teach (if teacher)
    courses_taught = []
    if getattr(profile, "role", None) == "teacher":
        courses_taught = (
            Course.objects
            .filter(teacher=profile)
            .order_by("title")
        )

    # Courses they are enrolled in (if student)
    enrolled_courses = (
        Course.objects
        .filter(enrollments__student=profile, enrollments__status=Enrollment.Status.ACTIVE)
        .order_by("title")
        .distinct()
    )

    return render(request, "accounts/public_profile.html", {
        "profile": profile,
        "statuses": statuses,
        "courses_taught": courses_taught,
        "enrolled_courses": enrolled_courses,
    })

@login_required
def user_directory(request):
    q = (request.GET.get("q") or "").strip()
    role = (request.GET.get("role") or "").strip()

    users = User.objects.all().order_by("username")

    if role in {"student", "teacher"}:
        users = users.filter(role=role)

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )

    # optional: hide self in the list
    users = users.exclude(id=request.user.id)

    return render(request, "accounts/user_directory.html", {
        "users": users,
        "q": q,
        "role": role,
    })
