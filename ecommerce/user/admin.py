from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
)
from .models import User


class CustomUserAdmin(BaseUserAdmin):
    ordering = ["id"]

    list_display = [
        "name",
        "email",
        "id",
    ]

    fieldsets = (
        ("Credentials", {"fields": ("email", "name", "password")}),
        ("Dates", {"fields": ("last_login",)}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "user_permissions")},
        ),
        ("Groups", {"fields": ("groups",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": [
                    "email",
                    "name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                    "groups",
                ],
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
