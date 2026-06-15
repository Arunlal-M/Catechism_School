"""
Shared base models.

WHY ABSTRACT BASE MODELS?
─────────────────────────
Many models need created_at, updated_at, created_by, updated_by fields.
Instead of copy-pasting these to every model, we define them once in
TimeStampedModel. Any model that inherits from it gets these fields
automatically. `abstract = True` means Django won't create a database
table for TimeStampedModel itself — it only adds its fields to children.

AuditLog is a concrete model that stores a history of who did what.
"""

from django.conf import settings
from django.db import models

from .constants import AUDIT_ACTION_CHOICES


class TimeStampedModel(models.Model):
    """
    Abstract base model that adds audit timestamps and user tracking.

    Every model that needs "who created/updated this and when" should
    inherit from this instead of models.Model.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # WHO created/updated — nullable because some records are system-generated
    # (e.g., from imports) or created before we had auth.
    # WHY settings.AUTH_USER_MODEL instead of importing User directly?
    # Because Django's User model might not be loaded yet when this file
    # is first read. Using the string reference is the safe pattern.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",  # e.g., studentprofile_created
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True  # No database table for this model


class AuditLog(models.Model):
    """
    Tracks important actions: creates, updates, deletes, imports, exports.

    WHY a separate table?
    - created_by/updated_by on each model tells you the LATEST state.
    - AuditLog tells you the FULL HISTORY: who changed what, when, and
      what the old/new values were.

    WHY JSONField for `changes`?
    - The structure of changes varies per model (different fields).
    - JSON is flexible and human-readable in Django admin.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=AUDIT_ACTION_CHOICES)
    model_name = models.CharField(max_length=100)      # e.g., "StudentProfile"
    object_id = models.PositiveIntegerField(null=True, blank=True)
    changes = models.JSONField(default=dict, blank=True)  # {"field": {"old": x, "new": y}}
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["model_name", "object_id"]),
        ]

    def __str__(self):
        return f"{self.action} {self.model_name} #{self.object_id} by {self.user}"
