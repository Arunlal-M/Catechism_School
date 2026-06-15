"""
Shared constants used across the project.

WHY A CONSTANTS FILE?
─────────────────────
Instead of scattering magic strings like "male", "female", "admin"
throughout models, forms, and templates, we define them once here.
Django's `choices` parameter uses tuples of (stored_value, display_label).
"""

# ──────────────────────────────────────────────
# User roles
# ──────────────────────────────────────────────
ROLE_ADMIN = "admin"
ROLE_STUDENT = "student"

ROLE_CHOICES = [
    (ROLE_ADMIN, "Admin / Teacher"),
    (ROLE_STUDENT, "Student"),
]

# ──────────────────────────────────────────────
# Gender
# ──────────────────────────────────────────────
GENDER_MALE = "M"
GENDER_FEMALE = "F"
GENDER_OTHER = "O"

GENDER_CHOICES = [
    (GENDER_MALE, "Male"),
    (GENDER_FEMALE, "Female"),
    (GENDER_OTHER, "Other"),
]

# ──────────────────────────────────────────────
# Student record status
# ──────────────────────────────────────────────
STATUS_ACTIVE = "active"
STATUS_PENDING = "pending"
STATUS_INACTIVE = "inactive"

STATUS_CHOICES = [
    (STATUS_ACTIVE, "Active"),
    (STATUS_PENDING, "Pending"),
    (STATUS_INACTIVE, "Inactive"),
]

# ──────────────────────────────────────────────
# Import batch status
# ──────────────────────────────────────────────
IMPORT_PENDING = "pending"
IMPORT_PROCESSING = "processing"
IMPORT_COMPLETED = "completed"
IMPORT_FAILED = "failed"

IMPORT_STATUS_CHOICES = [
    (IMPORT_PENDING, "Pending"),
    (IMPORT_PROCESSING, "Processing"),
    (IMPORT_COMPLETED, "Completed"),
    (IMPORT_FAILED, "Failed"),
]

# ──────────────────────────────────────────────
# Import row status
# ──────────────────────────────────────────────
ROW_SUCCESS = "success"
ROW_FAILED = "failed"
ROW_DUPLICATE = "duplicate"

ROW_STATUS_CHOICES = [
    (ROW_SUCCESS, "Success"),
    (ROW_FAILED, "Failed"),
    (ROW_DUPLICATE, "Duplicate"),
]

# ──────────────────────────────────────────────
# Audit log actions
# ──────────────────────────────────────────────
ACTION_CREATE = "create"
ACTION_UPDATE = "update"
ACTION_DELETE = "delete"
ACTION_IMPORT = "import"
ACTION_EXPORT = "export"

AUDIT_ACTION_CHOICES = [
    (ACTION_CREATE, "Create"),
    (ACTION_UPDATE, "Update"),
    (ACTION_DELETE, "Delete"),
    (ACTION_IMPORT, "Import"),
    (ACTION_EXPORT, "Export"),
]
