"""
Admin config for master data models.

WHY register master data in admin?
──────────────────────────────────
Even though we build a custom Master Data page in the app, the Django
admin is a reliable fallback for superusers to manage lookup tables
directly. It's also useful for debugging.
"""

from django.contrib import admin

from .models import Division, Provision, SchoolClass, Unit


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "is_active"]
    list_filter = ["is_active"]
    list_editable = ["order", "is_active"]  # Edit directly in list view
    search_fields = ["name"]


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    list_editable = ["is_active"]
    search_fields = ["name"]


@admin.register(Provision)
class ProvisionAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    list_editable = ["is_active"]
    search_fields = ["name"]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["name", "provision", "is_active"]
    list_filter = ["provision", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["name", "provision__name"]
