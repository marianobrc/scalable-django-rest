"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import View
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView

router = DefaultRouter(trailing_slash=True)


# status endpoint for health checks
class StatusView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"status": "OK"}, status=200)


urlpatterns = [
    # Health checks endpoint called by the load balancer
    path("status/", view=StatusView.as_view(), name="status"),
    # JWT authentication using dj-rest-auth endpoints (login, logout, user details..)
    # https://dj-rest-auth.readthedocs.io/en/latest/api_endpoints.html
    path("api/v1/rest-auth/", include("dj_rest_auth.urls")),
    path("api/v1/rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "api/v1/rest-auth/password_reset/",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "api/v1/rest-auth/password_reset_confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # All Business APIs are located at this root.
    # http://localhost:8000/api/<router-viewsets>'
    # Notice this is the router created above.
    path("api/v1/", include(router.urls)),
    # The DRF browsable API requires session authentication to work.
    path("api-auth/", include("rest_framework.urls")),
    # Django Administration
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns.append(*staticfiles_urlpatterns())
    urlpatterns.append(
        path(r"silk/", include("silk.urls", namespace="silk")),
    )
