from django.contrib import admin
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from issues.api import (
    IssuesAPI,
    IssuesRetrieveUpdateDeleteAPI,
    issues_close,
    issues_take,
    messages_api_dispatcher,
)
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from users.api import (
    UserActivateAPIView,
    UserCreateAPI,
    UserDestroyAPI,
    UserRetrieveUpdateAPI,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Support API (education project)",
        default_version="v1",
        description=(
            "Suport is a educational platform connecting junior developers (juniors) with "
            "experienced developers (seniors). Juniors can post their issues and questions,"
            "while seniors provide answers and guidance, fostering skill development and community support."
        ),
        contact=openapi.Contact(email="chaiunmykola@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    # users
    path("users/", UserCreateAPI.as_view()),
    path("users/<int:id>", UserRetrieveUpdateAPI.as_view()),
    path("users/delete/<int:id>", UserDestroyAPI.as_view()),
    path("users/activate", UserActivateAPIView.as_view()),
    # issues
    path("issues/", IssuesAPI.as_view()),
    path("issues/<int:id>", IssuesRetrieveUpdateDeleteAPI.as_view()),
    path("issues/<int:id>/close", issues_close),
    path("issues/<int:id>/take", issues_take),
    # messages
    path("issues/<int:issue_id>/messages", messages_api_dispatcher),
    # Authentication
    # path("auth/token/", token_obtain_pair),
    path("auth/token/", TokenObtainPairView.as_view()),
    # OpenAPI
    path(
        "swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
