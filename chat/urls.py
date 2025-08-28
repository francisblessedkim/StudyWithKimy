from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path('history/<str:username>/', views.chat_history, name='chat_history'),
    path('<str:username>/', views.chat_room, name='room'),
]
