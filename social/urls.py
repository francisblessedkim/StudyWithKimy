from django.urls import path
from . import views

app_name = "social"

urlpatterns = [
    path("status/new/", views.post_status, name="post_status"),
    path("status/<int:pk>/delete/", views.delete_status, name="delete_status"),
]
