"""
Global context processor — adds variables to EVERY template.

WHY?
────
Instead of passing `school_name` in every single view, we add it once
here. Django calls this function for every request and merges the
returned dict into the template context.

Registered in base.py → TEMPLATES → context_processors.
"""


def global_context(request):
    """Variables available in every template as {{ school_name }}, etc."""
    return {
        "school_name": "Catechism 2025-2026",
        "current_year": __import__("datetime").date.today().year,
    }


def notifications_processor(request):
    from django.contrib.auth import get_user_model
    from students.models import StudentProfile
    from common.constants import ROLE_ADMIN

    User = get_user_model()
    
    if not request.user.is_authenticated:
        return {}

    pending_admins = 0
    pending_students = 0

    if request.user.is_superuser:
        pending_admins = User.objects.filter(role=ROLE_ADMIN, is_active=False).count()
        
    if request.user.role == ROLE_ADMIN or request.user.is_superuser:
        pending_students = StudentProfile.objects.filter(status='pending').count()

    return {
        'pending_admins_count': pending_admins,
        'pending_students_count': pending_students,
        'total_notifications': pending_admins + pending_students
    }
