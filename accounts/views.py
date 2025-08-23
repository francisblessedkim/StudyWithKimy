from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from courses.models import Course, Enrollment, Material
from social.models import StatusUpdate, Notification

User = get_user_model()

def public_profile(request, username):
    profile = get_object_or_404(User, username=username)
    statuses = StatusUpdate.objects.filter(author=profile)[:20]
    # show public info and course titles (no private grades etc.)
    enrolled_titles = (Course.objects
                       .filter(enrollments__student=profile, enrollments__status="active")
                       .values_list("title", flat=True)
                       .distinct())
    return render(request, "accounts/public_profile.html", {
        "profile": profile,
        "statuses": statuses,
        "enrolled_titles": enrolled_titles,
    })

# @login_required
# def dashboard(request):
#     me = request.user
#     my_courses_taught = Course.objects.filter(teacher=me) if getattr(me, "role", None) == "teacher" else []
#     my_enrollments = Enrollment.objects.select_related("course").filter(student=me, status="active")
#     my_materials = Material.objects.filter(course__teacher=me)[:10] if getattr(me, "role", None) == "teacher" else []
#     notifications = Notification.objects.filter(recipient=me, is_read=False)[:10]
#     return render(request, "accounts/dashboard.html", {
#         "my_courses_taught": my_courses_taught,
#         "my_enrollments": my_enrollments,
#         "my_materials": my_materials,
#         "notifications": notifications,
#     })

@login_required
def dashboard(request):
    me = request.user
    my_courses_taught = Course.objects.filter(teacher=me) if getattr(me, "role", None) == "teacher" else []
    my_enrollments = Enrollment.objects.select_related("course").filter(student=me, status="active")
    my_materials = Material.objects.filter(course__teacher=me)[:10] if getattr(me, "role", None) == "teacher" else []
    notifications = Notification.objects.filter(recipient=me, is_read=False)[:10]
    
    # Add this line to get all users except the current one
    users = User.objects.exclude(id=me.id)

    return render(request, "accounts/dashboard.html", {
        "my_courses_taught": my_courses_taught,
        "my_enrollments": my_enrollments,
        "my_materials": my_materials,
        "notifications": notifications,
        "users": users,  # 👈 Pass to template
    })
