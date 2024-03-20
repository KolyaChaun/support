from django.contrib import admin
from django.urls import path

from issues.api import create_new_issue, get_issue

urlpatterns = [
    path("admin/", admin.site.urls),
    path("create-issue", create_new_issue),
    path("get-issue", get_issue),
]
