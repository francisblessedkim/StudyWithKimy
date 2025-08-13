from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("Study With Kimy — it works!")

urlpatterns = [
    path("", home, name="home"),
]
