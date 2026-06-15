"""
Authentication views — login, logout, profile, role-based redirect.

KEY DJANGO CONCEPT: Class-Based Views (CBVs)
─────────────────────────────────────────────
Django offers function-based views (def my_view(request):) and
class-based views (class MyView(View):).

CBVs are better when:
  - You need to handle GET/POST differently (CBV has get()/post() methods)
  - You want to reuse logic via mixins
  - Django provides a built-in CBV for exactly what you need

We use Django's built-in LoginView for login (why rewrite authentication?)
and custom views for the rest.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from common.constants import ROLE_ADMIN, ROLE_STUDENT
from common.mixins import SuperuserRequiredMixin
from common.emails import send_admin_approval_request, send_account_status_update
from .forms import CustomUserCreationForm, EmailLoginForm, UserProfileForm
from .models import User


class CustomLoginView(LoginView):
    """
    Login page using our email-based form.

    HOW LoginView WORKS:
    1. GET → renders the template with the form
    2. POST → validates credentials
    3. Success → redirects to LOGIN_REDIRECT_URL (or 'next' param)
    4. Failure → re-renders with error messages

    We override get_redirect_url() to send admins and students to
    different dashboards.
    """
    template_name = "accounts/login.html"
    form_class = EmailLoginForm

    def get_redirect_url(self):
        """Redirect based on role after successful login."""
        url = super().get_redirect_url()
        if url:
            return url
        # Role-based redirect
        if self.request.user.is_authenticated:
            if self.request.user.role == ROLE_ADMIN:
                return "/dashboard/"
            return "/student/dashboard/"
        return "/dashboard/"  # Fallback for GET request template rendering

    def dispatch(self, request, *args, **kwargs):
        """If already logged in, redirect to dashboard."""
        if request.user.is_authenticated:
            if request.user.role == ROLE_ADMIN:
                return redirect("/dashboard/")
            return redirect("/student/dashboard/")
        return super().dispatch(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    """Logout and redirect to login page."""
    next_page = "/accounts/login/"
    http_method_names = ['get', 'post', 'options']

    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        return redirect(self.next_page)


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    View/edit own profile (name, email).

    HOW UpdateView WORKS:
    1. get_object() returns the object to edit (here: current user)
    2. GET → renders form pre-filled with current data
    3. POST → validates and saves changes
    4. Success → redirects to success_url
    """
    template_name = "accounts/profile.html"
    form_class = UserProfileForm
    success_url = "/accounts/profile/"

    def get_object(self, queryset=None):
        """Edit the currently logged-in user (not a URL pk)."""
        return self.request.user


class LandingPageView(TemplateView):
    """
    Landing page for the Catechism 2025-2026 application.
    Redirects authenticated users to their respective dashboards.
    """
    template_name = "landing.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == ROLE_ADMIN:
                return redirect("/dashboard/")
            return redirect("/student/dashboard/")
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    """
    Registration view for new users.
    Supports role-based registration via kwargs.
    """
    template_name = "accounts/register.html"
    form_class = CustomUserCreationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Ensure role is passed from URL kwarg
        kwargs['role'] = self.kwargs.get('role', ROLE_STUDENT)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.kwargs.get('role', ROLE_STUDENT)
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        if user.role == ROLE_ADMIN:
            user.is_active = False
            user.save()
            send_admin_approval_request(user)
            messages.success(self.request, "Admin account registered successfully. It is currently pending superadmin approval.")
            return redirect("landing")
        else:
            user.save()
            login(self.request, user)
            return redirect("/student/dashboard/")


# ═══════════════════════════════════════════════
# ADMIN CRUD & APPROVAL VIEWS (SUPERADMIN ONLY)
# ═══════════════════════════════════════════════

class AdminListView(SuperuserRequiredMixin, ListView):
    """List all admins and their status."""
    model = User
    template_name = "accounts/admin_list.html"
    context_object_name = "admins"

    def get_queryset(self):
        return User.objects.filter(role=ROLE_ADMIN).exclude(id=self.request.user.id).order_by("is_active", "first_name")


class AdminCreateView(SuperuserRequiredMixin, CreateView):
    """Superadmin creates a new admin."""
    model = User
    template_name = "accounts/admin_form.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("accounts:admin_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['role'] = ROLE_ADMIN
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True  # Superadmin created, so already active
        user.save()
        messages.success(self.request, f"Admin {user.get_full_name()} created successfully.")
        return redirect(self.success_url)


class AdminUpdateView(SuperuserRequiredMixin, UpdateView):
    """Edit/Deactivate an admin."""
    model = User
    template_name = "accounts/admin_form.html"
    fields = ["first_name", "last_name", "email", "is_active"]
    success_url = reverse_lazy("accounts:admin_list")

    def get_queryset(self):
        return User.objects.filter(role=ROLE_ADMIN).exclude(id=self.request.user.id)

    def form_valid(self, form):
        # Check if status changed to send email
        old_user = self.get_object()
        new_active = form.cleaned_data.get('is_active')
        user = form.save()
        
        if old_user.is_active != new_active:
            send_account_status_update(user, is_approved=new_active)
            status_word = "activated" if new_active else "deactivated"
            messages.success(self.request, f"Admin {user.get_full_name()} has been {status_word}.")
        else:
            messages.success(self.request, f"Admin {user.get_full_name()} updated successfully.")
            
        return redirect(self.success_url)


class AdminDeleteView(SuperuserRequiredMixin, DeleteView):
    """Delete an admin permanently."""
    model = User
    template_name = "accounts/admin_confirm_delete.html"
    success_url = reverse_lazy("accounts:admin_list")
    context_object_name = "admin_user"

    def get_queryset(self):
        return User.objects.filter(role=ROLE_ADMIN).exclude(id=self.request.user.id)

    def form_valid(self, form):
        user = self.get_object()
        messages.success(self.request, f"Admin {user.get_full_name()} was permanently deleted.")
        return super().form_valid(form)


class AdminApproveView(SuperuserRequiredMixin, View):
    """Quick POST view to approve an admin from the list."""
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, role=ROLE_ADMIN, is_active=False)
        user.is_active = True
        user.save()
        send_account_status_update(user, is_approved=True)
        messages.success(request, f"Admin {user.get_full_name()} has been approved and activated.")
        return redirect("accounts:admin_list")
