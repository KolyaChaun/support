from django.contrib import admin
from django.urls import path
from issues.api import (
    IssuesAPI,
    IssuesRetrieveUpdateDeleteAPI,
    issues_close,
    issues_take,
    messages_api_dispatcher,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from users.api import (
    UserActivateAPIView,
    UserCreateAPI,
    UserDestroyAPI,
    UserRetrieveUpdateAPI,
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
]
