from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth import get_user_model
from django.db.models import Q
from courses.models import Enrollment
from .models import StatusUpdate

User = get_user_model()

@login_required
def post_status(request):
    if request.method != "POST":
        return redirect("/dashboard/")
    text = (request.POST.get("text") or "").strip()
    next_url = request.POST.get("next") or "/dashboard/"
    if not text:
        messages.error(request, "Status cannot be empty.")
        return redirect(next_url)
    if len(text) > 280:  # <- your model’s limit
        messages.error(request, "Please keep status under 280 characters.")
        return redirect(next_url)
    StatusUpdate.objects.create(author=request.user, text=text)
    messages.success(request, "Status posted.")
    return redirect(next_url)

@login_required
def delete_status(request, pk):
    obj = get_object_or_404(StatusUpdate, pk=pk, author=request.user)
    next_url = request.POST.get("next") or "/dashboard/"
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Status deleted.")
    return redirect(next_url)

@login_required
def classmates_feed(request):
    me = request.user
    # Users who share a course with me (either I’m a student OR I’m the teacher)
    # 1) courses I’m enrolled on
    my_course_ids = Enrollment.objects.filter(student=me, status="active").values_list("course_id", flat=True)
    # classmates on those courses
    classmates_ids = Enrollment.objects.filter(course_id__in=my_course_ids, status="active")\
                                       .exclude(student_id=me.id).values_list("student_id", flat=True)

    # 2) if I’m a teacher, include my students on my courses
    if getattr(me, "role", None) == "teacher":
        teacher_student_ids = Enrollment.objects.filter(course__teacher=me, status="active")\
                                               .values_list("student_id", flat=True)
    else:
        teacher_student_ids = User.objects.none().values_list("id", flat=True)

    people_ids = set(list(classmates_ids) + list(teacher_student_ids))
    feed = StatusUpdate.objects.select_related("author").filter(author_id__in=people_ids).order_by("-created_at")[:100]

    return render(request, "social/feed.html", {"feed": feed})