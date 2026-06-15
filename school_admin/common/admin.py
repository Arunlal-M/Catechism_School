"""
Django admin configuration for the AuditLog model.

WHY REGISTER IN ADMIN?
──────────────────────
Django's admin site (at /admin/) gives you a free CRUD interface for
any registered model. For AuditLog, we make it read-only — admins
can view the history but not edit it (that would defeat the purpose).
"""

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Read-only admin view for audit logs.

    list_display: columns shown in the list view
    list_filter: sidebar filters for quick filtering
    search_fields: fields searchable via the search bar
    readonly_fields: prevents editing (it's an audit log!)
    """
    list_display = ["timestamp", "user", "action", "model_name", "object_id"]
    list_filter = ["action", "model_name", "timestamp"]
    search_fields = ["user__email", "model_name"]
    readonly_fields = [
        "user", "action", "model_name", "object_id", "changes", "timestamp",
    ]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        """Prevent manual creation — logs are system-generated."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing — logs are immutable."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion — logs are permanent."""
        return False
