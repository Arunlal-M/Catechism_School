"""Admin config for import batch models."""

from django.contrib import admin

from .models import AdmissionImportBatch, ImportRow


class ImportRowInline(admin.TabularInline):
    """Show individual rows within a batch — read-only."""
    model = ImportRow
    extra = 0
    readonly_fields = ["row_number", "raw_data", "status", "error_message", "student"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AdmissionImportBatch)
class AdmissionImportBatchAdmin(admin.ModelAdmin):
    list_display = [
        "id", "file_name", "uploaded_by", "total_rows",
        "success_count", "failed_count", "duplicate_count",
        "status", "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["file_name", "uploaded_by__email"]
    readonly_fields = [
        "uploaded_by", "file_name", "file", "total_rows",
        "success_count", "failed_count", "duplicate_count",
        "column_mapping", "created_at",
    ]
    inlines = [ImportRowInline]
