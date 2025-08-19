from django.urls import path
from django.http import HttpResponse
from . import views

def home(request):
    return HttpResponse("Study With Kimy — it works!")

urlpatterns = [
    path("", home, name="home"),
    path("u/<str:username>/", views.public_profile, name="public_profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
