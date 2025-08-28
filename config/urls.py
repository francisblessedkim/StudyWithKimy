# config/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Built-in auth pages: /accounts/login/, /accounts/logout/, etc.
    path("accounts/", include("django.contrib.auth.urls")),

    # Accounts app at ROOT => /, /signup/, /dashboard/, /u/<username>/
    path("", include("accounts.urls")),

    # Other apps (keep as you currently use them)
    path("", include("courses.urls")),
    path("", include("social.urls")),
    path("chat/", include("chat.urls")),

    # API + docs
    path("api/", include("api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
