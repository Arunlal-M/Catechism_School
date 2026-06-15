"""
View mixins — reusable access-control logic for class-based views.

WHY MIXINS?
───────────
Django's class-based views use Python's multiple inheritance. A mixin
is a small class that adds ONE specific behavior. You combine them:

    class MyView(AdminRequiredMixin, ListView):
        ...

This view now requires admin login AND shows a list. Mixins avoid
duplicating permission checks across dozens of views.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

from common.constants import ROLE_ADMIN


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Only allow users with role='admin' to access the view.

    HOW IT WORKS:
    1. LoginRequiredMixin checks if user is logged in → redirects to login if not
    2. UserPassesTestMixin calls test_func() → returns 403 if it returns False
    """

    def test_func(self):
        return self.request.user.role == ROLE_ADMIN

    def handle_no_permission(self):
        """If logged in but not admin, redirect to student dashboard."""
        if self.request.user.is_authenticated:
            return redirect("students:student_dashboard")
        return super().handle_no_permission()


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Only allow superusers to access the view.
    """
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect("/dashboard/")
        return super().handle_no_permission()
