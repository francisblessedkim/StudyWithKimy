from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import StatusUpdate

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
