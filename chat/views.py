from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import ChatMessage

User = get_user_model()

@login_required
def chat_history(request, username):
    try:
        other_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    messages = ChatMessage.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by("timestamp")

    history = [
        {"sender": m.sender.username, "message": m.message, "timestamp": m.timestamp.isoformat()}
        for m in messages
    ]
    return JsonResponse({"messages": history})

# NEW: thin HTML page that hosts the WebSocket chat UI
# @login_required
# def chat_room(request, username):
#     recipient = get_object_or_404(User, username=username)
#     return render(request, "chat/room.html", {"recipient": recipient})
@login_required
def chat_room(request, username):
    recipient = get_object_or_404(User, username=username)
    # Set this to whatever your Channels route expects:
    # Common choices:
    #   "/ws/chat/"               -> re_path(r"ws/chat/(?P<username>[^/]+)/$", ...)
    #   "/ws/chatroom/"           -> re_path(r"ws/chatroom/(?P<username>[^/]+)/$", ...)
    ws_base = "/ws/chat/"
    return render(request, "chat/room.html", {"recipient": recipient, "ws_base": ws_base})

