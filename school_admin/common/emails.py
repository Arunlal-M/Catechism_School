from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from common.constants import ROLE_ADMIN

User = get_user_model()


def send_admin_approval_request(new_admin):
    """Notify all superadmins that a new admin has registered and is pending approval."""
    superadmins = User.objects.filter(is_superuser=True)
    recipient_list = [admin.email for admin in superadmins if admin.email]
    
    if not recipient_list:
        return

    subject = f"New Admin Registration Pending Approval: {new_admin.get_full_name()}"
    message = (
        f"A new admin account has been registered and is waiting for your approval.\n\n"
        f"Name: {new_admin.get_full_name()}\n"
        f"Email: {new_admin.email}\n\n"
        f"Please log in to the admin dashboard and navigate to the Manage Admins section to review this request."
    )
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


def send_student_approval_request(student_profile):
    """Notify all admins and superadmins that a new student profile has been submitted."""
    admins = User.objects.filter(role=ROLE_ADMIN, is_active=True)
    recipient_list = [admin.email for admin in admins if admin.email]
    
    if not recipient_list:
        return

    subject = f"New Student Profile Pending Approval: {student_profile.student_name}"
    message = (
        f"A new student has submitted their profile and it is pending approval.\n\n"
        f"Name: {student_profile.student_name}\n"
        f"Email: {student_profile.email}\n\n"
        f"Please log in to the dashboard and review pending students."
    )
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


def send_account_status_update(user, is_approved):
    """Notify a user (admin or student) that their account status has changed."""
    if not user.email:
        return

    status_text = "approved and activated" if is_approved else "rejected/deactivated"
    subject = f"Your account has been {status_text}"
    message = (
        f"Hello {user.get_full_name()},\n\n"
        f"Your account on the Catechism 2025-2026 portal has been {status_text}.\n"
    )
    if is_approved:
        message += "You can now log in and access your dashboard.\n"
    else:
        message += "If you believe this is an error, please contact the administration.\n"
        
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
