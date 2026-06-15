"""
Development settings — extends base.py

WHY A SEPARATE FILE?
────────────────────
Development needs things production doesn't:
  - DEBUG = True (detailed error pages)
  - django-debug-toolbar (SQL query inspector)
  - Console email backend (prints emails to terminal)

This file imports EVERYTHING from base.py, then overrides specific values.
"""

from .base import *  # noqa: F401,F403

# ──────────────────────────────────────────────
# Override: always debug in development
# ──────────────────────────────────────────────
DEBUG = True

# ──────────────────────────────────────────────
# Debug Toolbar
# ──────────────────────────────────────────────
# WHY insert at position 0? Debug toolbar needs to wrap all other middleware
# to accurately measure their execution time.
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

# Only show toolbar for these IPs
INTERNAL_IPS = ["127.0.0.1"]

# ──────────────────────────────────────────────
# Email — print to console instead of sending
# ──────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
