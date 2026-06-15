"""
Custom User model — email-based authentication with roles.

WHY A CUSTOM USER MODEL?
────────────────────────
Django's built-in User uses username for login. We want:
  1. Email-based login (more natural for schools)
  2. A 'role' field (admin vs student)

IMPORTANT: AUTH_USER_MODEL must be set in settings BEFORE the first
migration. If you forget and migrate with Django's default User, you'll
have to reset the entire database. That's why we set it early in base.py.

HOW ABSTRACTUSER WORKS:
  AbstractUser gives us everything the default User has (password hashing,
  permissions, is_active, etc.) and lets us add/override fields.
  We override USERNAME_FIELD to use email instead of username.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from common.constants import ROLE_ADMIN, ROLE_CHOICES, ROLE_STUDENT


class UserManager(BaseUserManager):
    """
    Custom manager because we removed the username field.

    WHY?
    Django's default UserManager.create_user() expects a username argument.
    Since we use email as the identifier, we need a custom manager that
    takes email instead.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create a regular user with email and password."""
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a superuser (for `python manage.py createsuperuser`).
        Superusers are always admins with full Django admin access.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", ROLE_ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user: email login + role field.

    FIELDS INHERITED FROM AbstractUser:
      - password, first_name, last_name, is_active, is_staff,
        is_superuser, date_joined, last_login, groups, user_permissions

    FIELDS WE ADD:
      - email (made unique, used as login identifier)
      - role (admin or student)

    FIELDS WE REMOVE:
      - username (replaced by email)
    """
    # Override: make email unique and required
    email = models.EmailField("email address", unique=True)

    # Remove username field entirely
    username = None

    # Add role field
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT,
    )

    # Tell Django to use email for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]  # Asked during createsuperuser

    # Use our custom manager
    objects = UserManager()

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_admin(self):
        """Convenience property for templates: {% if user.is_admin %}"""
        return self.role == ROLE_ADMIN

    @property
    def is_student_role(self):
        """Convenience property for templates: {% if user.is_student_role %}"""
        return self.role == ROLE_STUDENT
