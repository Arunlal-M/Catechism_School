"""
Admin config for custom User model.

WHY CUSTOMIZE?
──────────────
Django's default UserAdmin is designed for the built-in User (with username).
Since we use email + role, we need to customize:
  - Which fields show in the list view
  - Which fields show in the add/edit forms
  - Which fields are searchable/filterable
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for our email-based User model.

    WHY override fieldsets?
    BaseUserAdmin expects a 'username' field. We replaced it with 'email'
    and added 'role', so we need to update the form layout.
    """
    # Columns in the user list page
    list_display = ["email", "first_name", "last_name", "role", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]

    # Fields shown when EDITING an existing user
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Role", {"fields": ("role",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fields shown when CREATING a new user
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )
