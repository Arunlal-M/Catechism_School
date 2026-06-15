"""
Admin config for student models.

KEY FEATURE: Inlines
────────────────────
Django admin 'inlines' let you edit related models on the same page.
Instead of editing StudentProfile, ParentInfo, and CatechismInfo on
3 separate pages, we show them all together on one form.

TabularInline = compact table layout
StackedInline = full-width form layout (better for many fields)
"""

from django.contrib import admin

from .models import CatechismInfo, ParentInfo, StudentProfile


class ParentInfoInline(admin.StackedInline):
    """
    Show parent info as part of the student edit page.
    extra=1 means show 1 blank form if no parent info exists yet.
    """
    model = ParentInfo
    extra = 0
    can_delete = False


class CatechismInfoInline(admin.StackedInline):
    """Show catechism info as part of the student edit page."""
    model = CatechismInfo
    extra = 0
    can_delete = False


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Full-featured admin for student records.

    list_display: what columns to show in the list
    list_filter: sidebar filters
    search_fields: the search box searches these fields
    inlines: show ParentInfo and CatechismInfo on the same page
    readonly_fields: auto-generated fields that shouldn't be edited
    """
    list_display = [
        "student_number",
        "student_name",
        "school_class",
        "division",
        "status",
        "attended_catechism",
        "created_at",
    ]
    list_filter = ["status", "school_class", "division", "attended_catechism", "gender"]
    search_fields = [
        "student_name",
        "student_number",
        "email",
        "parent_info__father_name",
        "parent_info__mother_name",
        "parent_info__father_phone",
        "parent_info__mother_phone",
    ]
    readonly_fields = ["student_number", "created_at", "updated_at", "created_by", "updated_by"]
    inlines = [ParentInfoInline, CatechismInfoInline]

    # Organize fields into logical sections
    fieldsets = (
        ("Student Info", {
            "fields": (
                "student_number", "student_name", "email",
                "gender", "date_of_birth",
            ),
        }),
        ("Class & Division", {
            "fields": ("school_class", "division"),
        }),
        ("Catechism", {
            "fields": ("attended_catechism",),
        }),
        ("Address & Notes", {
            "fields": ("residential_address", "remarks"),
        }),
        ("Status & Account", {
            "fields": ("status", "user"),
        }),
        ("Audit", {
            "classes": ("collapse",),  # Collapsed by default
            "fields": ("created_at", "updated_at", "created_by", "updated_by"),
        }),
    )

    def save_model(self, request, obj, form, change):
        """Auto-set created_by / updated_by when saving from admin."""
        if not change:  # Creating new
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
