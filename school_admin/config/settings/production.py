"""
Production settings — extends base.py

WHY A SEPARATE FILE?
────────────────────
Production needs maximum security and performance:
  - DEBUG = False (prevent leaking stack traces)
  - Strict ALLOWED_HOSTS
  - Security headers (HSTS, secure cookies)
  - Real email backend (SMTP)
"""

from .base import *  # noqa: F401,F403

# ──────────────────────────────────────────────
# Security Overrides
# ──────────────────────────────────────────────
DEBUG = False

# Must be set in .env in production!
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# HTTPS / Security Headers
# WHY? Forces browsers to only use HTTPS, prevents clickjacking, 
# and prevents cookies from being read over HTTP.
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ──────────────────────────────────────────────
# Email (Real SMTP)
# ──────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.sendgrid.net")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@school.com")

# ──────────────────────────────────────────────
# Static Files Storage (WhiteNoise)
# ──────────────────────────────────────────────
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

