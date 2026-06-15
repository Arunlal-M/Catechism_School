"""
Shared validators used across models and forms.

WHY SEPARATE VALIDATORS?
────────────────────────
Django lets you validate in models, forms, or standalone functions.
Standalone validators are the most reusable — you can attach the same
validator to a model field AND a form field without duplicating logic.

Each validator is a function that takes a value and raises
ValidationError if the value is invalid.
"""

import re
from datetime import date

from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """
    Accept 10-digit Indian phone numbers, optionally with +91 prefix.
    Examples: 9876543210, +919876543210, 09876543210

    WHY regex? Phone formats vary. This is intentionally lenient
    (digits only, 10-13 chars) to avoid rejecting valid numbers.
    """
    cleaned = re.sub(r"[\s\-\(\)]+", "", value)  # Strip spaces, dashes, parens
    if not re.match(r"^(\+91|0)?[6-9]\d{9}$", cleaned):
        raise ValidationError(
            "Enter a valid Indian phone number (10 digits, starting with 6-9)."
        )


def validate_not_future_date(value):
    """
    Date of birth cannot be in the future.

    WHY a separate validator? This is a business rule, not a format check.
    Django's DateField already handles format validation.
    """
    if value > date.today():
        raise ValidationError("Date of birth cannot be in the future.")


def validate_not_empty(value):
    """Reject whitespace-only strings."""
    if isinstance(value, str) and not value.strip():
        raise ValidationError("This field cannot be blank or whitespace only.")
