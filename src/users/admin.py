from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "date_joined",
    ]
    exclude = ["user_permissions", "groups"]
    readonly_fields = [
        "password",
        "date_joined",
        "last_login",
        "is_superuser",
        "email",
    ]
