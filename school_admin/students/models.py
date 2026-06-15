"""
Student data models — the core of the application.

MODEL DESIGN DECISIONS:
───────────────────────
1. StudentProfile is the main record. It links to:
   - ParentInfo (one-to-one) — father/mother details
   - CatechismInfo (one-to-one) — catechism teacher, provision, unit

2. WHY split into 3 models instead of one big table?
   - Keeps each model focused and readable
   - ParentInfo and CatechismInfo can be optional/incomplete
   - Easier to extend later (e.g., add a second guardian)
   - Each model stays under ~10 fields (maintainable)

3. StudentProfile.user is NULLABLE:
   - Records can exist before a student ever logs in
   - Admin creates records via form or Excel import
   - Student accounts are linked later if needed

4. student_number is AUTO-GENERATED:
   - Format: STU-YYYY-NNNN (e.g., STU-2026-0001)
   - Generated in the save() method
   - Unique constraint prevents duplicates
"""

from datetime import date

from django.conf import settings
from django.db import models

from admissions.models import Division, Provision, SchoolClass, Unit
from common.constants import GENDER_CHOICES, STATUS_ACTIVE, STATUS_CHOICES, STATUS_PENDING
from common.models import TimeStampedModel
from common.validators import validate_not_future_date, validate_phone_number


class StudentProfile(TimeStampedModel):
    """
    Main student record — one row per student.

    Inherits from TimeStampedModel, which adds:
      created_at, updated_at, created_by, updated_by
    """
    # ── Link to login account (optional) ──────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
        help_text="Linked user account for student login. Can be blank.",
    )

    # ── Personal info ─────────────────────────────────
    student_name = models.CharField(max_length=200)
    student_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,  # Blank allowed because we auto-generate it
        help_text="Auto-generated: STU-YYYY-NNNN",
    )
    email = models.EmailField(blank=True, default="")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(validators=[validate_not_future_date])

    # ── Class & Division (FKs to lookup tables) ───────
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,  # Can't delete a class that has students
        related_name="students",
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        related_name="students",
    )

    # ── Address ───────────────────────────────────────
    residential_address = models.TextField(blank=True, default="")

    # ── Catechism ─────────────────────────────────────
    attended_catechism = models.BooleanField(
        default=False,
        verbose_name="Attended Catechism?",
    )

    # ── Status ────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # ── Notes ─────────────────────────────────────────
    remarks = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student_name"]),
            models.Index(fields=["student_number"]),
            models.Index(fields=["email"]),
            models.Index(fields=["status"]),
            models.Index(fields=["school_class"]),
            models.Index(fields=["division"]),
        ]

    def __str__(self):
        return f"{self.student_name} ({self.student_number})"

    def save(self, *args, **kwargs):
        """
        Auto-generate student_number on first save.

        HOW IT WORKS:
        1. Only runs if student_number is blank (new record)
        2. Finds the last student_number for the current year
        3. Increments the sequence number
        4. Format: STU-2026-0001, STU-2026-0002, etc.
        """
        if not self.student_number:
            self.student_number = self._generate_student_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_student_number():
        """Generate the next sequential student number for the current year."""
        current_year = date.today().year
        prefix = f"STU-{current_year}-"

        # Find the highest existing number for this year
        last = (
            StudentProfile.objects
            .filter(student_number__startswith=prefix)
            .order_by("-student_number")
            .values_list("student_number", flat=True)
            .first()
        )

        if last:
            # Extract the sequence part: "STU-2026-0042" → 42
            last_sequence = int(last.split("-")[-1])
            next_sequence = last_sequence + 1
        else:
            next_sequence = 1

        return f"{prefix}{next_sequence:04d}"

    @property
    def is_active(self):
        return self.status == STATUS_ACTIVE

    @property
    def is_pending(self):
        return self.status == STATUS_PENDING


class ParentInfo(models.Model):
    """
    Father and mother details — one-to-one with StudentProfile.

    WHY OneToOneField?
    ──────────────────
    Each student has exactly one ParentInfo record.
    OneToOneField = ForeignKey with unique=True.
    Access: student.parent_info (reverse) or parent_info.student (forward).
    """
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,  # Delete parent info when student is deleted
        related_name="parent_info",
    )

    # ── Father ────────────────────────────────────────
    father_name = models.CharField(max_length=200, blank=True, default="")
    father_occupation = models.ForeignKey(
        "admissions.Occupation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fathers"
    )
    father_phone = models.CharField(
        max_length=15,
        blank=True,
        default="",
        validators=[validate_phone_number],
    )

    # ── Mother ────────────────────────────────────────
    mother_name = models.CharField(max_length=200, blank=True, default="")
    mother_occupation = models.ForeignKey(
        "admissions.Occupation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mothers"
    )
    mother_phone = models.CharField(
        max_length=15,
        blank=True,
        default="",
        validators=[validate_phone_number],
    )

    class Meta:
        verbose_name = "Parent Information"
        verbose_name_plural = "Parent Information"
        indexes = [
            models.Index(fields=["father_name"]),
            models.Index(fields=["mother_name"]),
            models.Index(fields=["father_phone"]),
            models.Index(fields=["mother_phone"]),
        ]

    def __str__(self):
        return f"Parents of {self.student.student_name}"


class CatechismInfo(models.Model):
    """
    Catechism-related details — one-to-one with StudentProfile.

    Only relevant if the student attended catechism (attended_catechism=True).
    """
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="catechism_info",
    )

    catechism_teacher_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Catechism Teacher Name",
    )
    provision = models.ForeignKey(
        Provision,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catechism_students",
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="catechism_students",
    )

    class Meta:
        verbose_name = "Catechism Information"
        verbose_name_plural = "Catechism Information"
        indexes = [
            models.Index(fields=["catechism_teacher_name"]),
            models.Index(fields=["provision"]),
            models.Index(fields=["unit"]),
        ]

    def __str__(self):
        return f"Catechism info for {self.student.student_name}"
