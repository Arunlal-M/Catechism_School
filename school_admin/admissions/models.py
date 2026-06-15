"""
Master data models — dropdown values managed by admin.

WHY SEPARATE MODELS FOR DROPDOWNS?
───────────────────────────────────
Instead of storing "Class 5" as a text string on every student record
(which leads to typos like "class 5", "Class5", "Class Five"), we store
it once in a SchoolClass table and reference it by ID (Foreign Key).

Benefits:
  - No typos or inconsistencies
  - Admin can rename "Class 5" → "Grade 5" in one place
  - Easy to deactivate without deleting (is_active=False)
  - Enforces data integrity at the database level

PROVISION → UNIT HIERARCHY:
  A Provision (Pradeshikam) contains multiple Units.
  When creating a student record, you first pick the Provision,
  then pick a Unit within that Provision. This is a one-to-many
  relationship: Provision has many Units.
"""

from django.db import models


class SchoolClass(models.Model):
    """
    e.g., Class 1, Class 2, ... Class 12

    WHY 'order' field? So we can sort Class 1 before Class 2.
    Without it, alphabetical sorting puts "Class 10" before "Class 2".
    """
    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Sort order (lower number = appears first)",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name


class Division(models.Model):
    """
    e.g., A, B, C

    Division is independent of Class — any class can have any division.
    """
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Occupation(models.Model):
    """
    Master data for parent occupations.
    e.g., Engineer, Doctor, Business, Unemployed.
    """
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Occupation"
        verbose_name_plural = "Occupations"

    def __str__(self):
        return self.name


class Provision(models.Model):
    """
    Pradeshikam — a regional administrative grouping.
    Contains multiple Units.
    """
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Provision (Pradeshikam)"
        verbose_name_plural = "Provisions (Pradeshikam)"

    def __str__(self):
        return self.name


class Unit(models.Model):
    """
    A Unit belongs to a Provision.

    WHY ForeignKey?
    ───────────────
    One Provision has many Units. When the admin picks a Provision in
    the student form, the Unit dropdown should filter to show only
    units under that Provision. The FK enforces this relationship.

    on_delete=CASCADE: if a Provision is deleted, its Units go too.
    (In practice we'd deactivate, not delete — but the FK needs a rule.)
    """
    name = models.CharField(max_length=100)
    provision = models.ForeignKey(
        Provision,
        on_delete=models.CASCADE,
        related_name="units",  # provision.units.all() gives all units
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["provision__name", "name"]
        # Same unit name can't appear twice under the same provision
        unique_together = ["name", "provision"]

    def __str__(self):
        return f"{self.name} ({self.provision.name})"
