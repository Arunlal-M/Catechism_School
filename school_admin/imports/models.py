"""
Import/Export models — track Excel upload batches and individual rows.

WHY TRACK IMPORTS?
──────────────────
When an admin uploads an Excel file with 500 students:
  - Some rows succeed, some fail validation, some are duplicates
  - The admin needs to see what happened to each row
  - They need to download just the failed rows to fix and re-upload

AdmissionImportBatch = one uploaded file
ImportRow = one row from that file

WHY store raw_data as JSON?
  - Each Excel file might have different columns
  - We store the raw data exactly as uploaded (for debugging)
  - After column mapping, we know which JSON key maps to which field
"""

from django.conf import settings
from django.db import models

from common.constants import (
    IMPORT_PENDING,
    IMPORT_STATUS_CHOICES,
    ROW_STATUS_CHOICES,
)


class AdmissionImportBatch(models.Model):
    """
    One uploaded Excel file = one batch.

    Tracks: who uploaded, how many rows succeeded/failed, column mapping.
    """
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="import_batches",
    )
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="imports/")   # Actual file stored in media/imports/
    total_rows = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    duplicate_count = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=IMPORT_STATUS_CHOICES,
        default=IMPORT_PENDING,
    )
    # Stores the admin's column mapping: {"Excel Column Name": "db_field_name"}
    column_mapping = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Import Batch"
        verbose_name_plural = "Import Batches"

    def __str__(self):
        return f"Batch #{self.pk} — {self.file_name} ({self.status})"


class ImportRow(models.Model):
    """
    One row from an uploaded Excel file.

    Stores the raw data, validation result, and error message.
    If successful, links to the created StudentProfile.
    """
    batch = models.ForeignKey(
        AdmissionImportBatch,
        on_delete=models.CASCADE,
        related_name="rows",
    )
    row_number = models.PositiveIntegerField()
    raw_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=ROW_STATUS_CHOICES)
    error_message = models.TextField(blank=True, default="")

    # Link to created student (only set on success)
    student = models.ForeignKey(
        "students.StudentProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["row_number"]

    def __str__(self):
        return f"Row {self.row_number} of Batch #{self.batch_id} — {self.status}"
