from django.urls import path
from django.http import HttpResponse
from . import views

def home(request):
    return HttpResponse("Study With Kimy — it works!")

urlpatterns = [
     path('signup/', views.signup, name='signup'),
    path("", views.landing_page, name="landing_page"),
    path("u/<str:username>/", views.public_profile, name="public_profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("u/<str:username>/", views.public_profile, name="public_profile"),
    path("users/", views.user_directory, name="user_directory"),
]
