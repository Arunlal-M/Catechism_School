"""
Student views — CRUD, dashboard, search, and student self-service.

VIEW TYPES USED:
────────────────
- ListView: paginated list with search/filter (StudentListView)
- DetailView: single record read-only view (StudentDetailView)
- CreateView: form to create a new record (StudentCreateView)
- UpdateView: form to edit an existing record (StudentUpdateView)
- DeleteView: confirmation + delete (StudentDeleteView)
- TemplateView: static/dashboard pages (StudentDashboardView)

PERMISSION PATTERN:
  AdminRequiredMixin → only admin role can access
  LoginRequiredMixin → any logged-in user can access
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from admissions.models import Division, Provision, SchoolClass
from common.constants import GENDER_CHOICES, STATUS_CHOICES, STATUS_INACTIVE
from common.mixins import AdminRequiredMixin
from .filters import filter_students
from .forms import (
    CatechismInfoForm,
    ParentInfoForm,
    ParentPhoneEditForm,
    StudentProfileForm,
    StudentSelfEditForm,
)
from .models import CatechismInfo, ParentInfo, StudentProfile
from common.emails import send_student_approval_request, send_account_status_update


# ═══════════════════════════════════════════════
# ADMIN VIEWS
# ═══════════════════════════════════════════════


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """
    Admin dashboard — summary stats and quick links.

    WHY get_context_data()?
    TemplateView renders a template with context. We override
    get_context_data() to add our stats to the context dict.
    """
    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_students"] = StudentProfile.objects.count()
        context["active_students"] = StudentProfile.objects.filter(status="active").count()
        context["pending_students"] = StudentProfile.objects.filter(status="pending").count()
        context["recent_students"] = StudentProfile.objects.order_by("-created_at")[:5]
        return context


class StudentListView(AdminRequiredMixin, ListView):
    """
    Paginated, searchable student list.

    HOW ListView WORKS:
    1. get_queryset() returns the list of objects
    2. paginate_by splits them into pages
    3. Template receives 'object_list' and 'page_obj' for pagination

    HTMX: If the request is from HTMX (live search), we return only
    the table partial instead of the full page. This is the core of
    HTMX — return HTML fragments, not full pages.
    """
    model = StudentProfile
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 25

    def get_queryset(self):
        """Apply search/filter from URL params."""
        qs = StudentProfile.objects.select_related(
            "school_class", "division", "parent_info", "catechism_info",
        )
        return filter_students(qs, self.request.GET)

    def get_context_data(self, **kwargs):
        """Add filter options to context for the filter dropdowns."""
        context = super().get_context_data(**kwargs)
        context["classes"] = SchoolClass.objects.filter(is_active=True)
        context["divisions"] = Division.objects.filter(is_active=True)
        context["provisions"] = Provision.objects.filter(is_active=True)
        context["status_choices"] = STATUS_CHOICES
        context["gender_choices"] = GENDER_CHOICES
        # Preserve current filter values in the form
        context["current_filters"] = self.request.GET
        return context

    def get_template_names(self):
        """Return partial template for HTMX requests."""
        if self.request.htmx:
            return ["students/partials/_student_table.html"]
        return [self.template_name]


class StudentDetailView(AdminRequiredMixin, DetailView):
    """
    Full student profile view — shows all data from all 3 models.

    select_related() joins the related tables in one SQL query
    instead of making separate queries for each (N+1 problem).
    """
    model = StudentProfile
    template_name = "students/student_detail.html"
    context_object_name = "student"

    def get_queryset(self):
        return StudentProfile.objects.select_related(
            "school_class", "division", "parent_info",
            "catechism_info", "catechism_info__provision", "catechism_info__unit",
            "user", "created_by", "updated_by",
        )


class StudentCreateView(AdminRequiredMixin, View):
    """
    Create a new student with parent info and catechism info.

    WHY a plain View instead of CreateView?
    ─────────────────────────────────────────
    CreateView handles ONE form for ONE model. We need THREE forms
    (student, parent, catechism) saved together in a transaction.
    A plain View with get()/post() gives us full control.

    WHY transaction.atomic()?
    If the parent form saves but catechism fails, we'd have orphan data.
    atomic() ensures ALL THREE save or NONE save.
    """
    template_name = "students/student_form.html"

    def get(self, request):
        context = {
            "student_form": StudentProfileForm(),
            "parent_form": ParentInfoForm(),
            "catechism_form": CatechismInfoForm(),
            "is_edit": False,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        student_form = StudentProfileForm(request.POST)
        parent_form = ParentInfoForm(request.POST)
        catechism_form = CatechismInfoForm(request.POST)

        if all([student_form.is_valid(), parent_form.is_valid(), catechism_form.is_valid()]):
            with transaction.atomic():
                # Save student first (generates student_number)
                student = student_form.save(commit=False)
                
                # Set status from button action
                status_action = request.POST.get("status_action")
                if status_action in [s[0] for s in STATUS_CHOICES]:
                    student.status = status_action
                    
                student.created_by = request.user
                student.updated_by = request.user
                student.save()

                # Save parent info linked to student
                parent = parent_form.save(commit=False)
                parent.student = student
                parent.save()

                # Save catechism info linked to student
                catechism = catechism_form.save(commit=False)
                catechism.student = student
                catechism.save()

            messages.success(request, f"Student {student.student_name} created successfully!")
            return redirect("students:student_detail", pk=student.pk)

        # If validation failed, re-render with errors
        context = {
            "student_form": student_form,
            "parent_form": parent_form,
            "catechism_form": catechism_form,
            "is_edit": False,
        }
        return render(request, self.template_name, context)


class StudentUpdateView(AdminRequiredMixin, View):
    """
    Edit an existing student — loads all 3 forms pre-filled.

    get_or_create() handles the case where a student was created via
    import but doesn't have parent/catechism records yet.
    """
    template_name = "students/student_form.html"

    def get_student(self, pk):
        return get_object_or_404(
            StudentProfile.objects.select_related("parent_info", "catechism_info"),
            pk=pk,
        )

    def get(self, request, pk):
        student = self.get_student(pk)
        parent, _ = ParentInfo.objects.get_or_create(student=student)
        catechism, _ = CatechismInfo.objects.get_or_create(student=student)

        context = {
            "student_form": StudentProfileForm(instance=student),
            "parent_form": ParentInfoForm(instance=parent),
            "catechism_form": CatechismInfoForm(instance=catechism),
            "is_edit": True,
            "student": student,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        student = self.get_student(pk)
        student._pre_save_status = student.status
        parent, _ = ParentInfo.objects.get_or_create(student=student)
        catechism, _ = CatechismInfo.objects.get_or_create(student=student)

        student_form = StudentProfileForm(request.POST, instance=student)
        parent_form = ParentInfoForm(request.POST, instance=parent)
        catechism_form = CatechismInfoForm(request.POST, instance=catechism)

        if all([student_form.is_valid(), parent_form.is_valid(), catechism_form.is_valid()]):
            with transaction.atomic():
                student = student_form.save(commit=False)
                
                # Set status from button action
                status_action = request.POST.get("status_action")
                if status_action in [s[0] for s in STATUS_CHOICES]:
                    student.status = status_action
                    
                student.updated_by = request.user
                student.save()
                parent_form.save()
                catechism_form.save()

            # Check if status changed from pending to active/inactive
            old_status = student._meta.model.objects.get(pk=student.pk).status if getattr(student, '_pre_save_status', None) is None else student._pre_save_status
            if old_status != student.status and student.user:
                if student.status == 'active':
                    send_account_status_update(student.user, is_approved=True)
                elif student.status == 'inactive':
                    send_account_status_update(student.user, is_approved=False)

            messages.success(request, f"Student {student.student_name} updated successfully!")
            return redirect("students:student_detail", pk=student.pk)

        context = {
            "student_form": student_form,
            "parent_form": parent_form,
            "catechism_form": catechism_form,
            "is_edit": True,
            "student": student,
        }
        return render(request, self.template_name, context)


class StudentDeleteView(AdminRequiredMixin, View):
    """
    Soft-delete a student (set status to 'inactive').

    WHY soft-delete?
    Hard delete (DELETE FROM ...) removes data forever. For a school,
    that's dangerous. Soft-delete sets status='inactive' so the record
    is hidden from normal views but can be recovered.
    """
    template_name = "students/student_confirm_delete.html"

    def get(self, request, pk):
        student = get_object_or_404(StudentProfile, pk=pk)
        return render(request, self.template_name, {"student": student})

    def post(self, request, pk):
        student = get_object_or_404(StudentProfile, pk=pk)
        student.status = STATUS_INACTIVE
        student.updated_by = request.user
        student.save()
        messages.success(request, f"Student {student.student_name} has been deactivated.")
        return redirect("students:student_list")


# ═══════════════════════════════════════════════
# STUDENT SELF-SERVICE VIEWS
# ═══════════════════════════════════════════════


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for logged-in students — shows their own profile."""
    template_name = "students/student_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["student"] = self.request.user.student_profile
        except StudentProfile.DoesNotExist:
            context["student"] = None
        return context


class StudentSelfFormView(LoginRequiredMixin, View):
    """
    Students can fill out or edit their own profile.
    If it's already active, they can't edit it.
    """
    template_name = "students/student_self_form.html"

    def get_student_objects(self, request):
        try:
            student = request.user.student_profile
            parent, _ = ParentInfo.objects.get_or_create(student=student)
            catechism, _ = CatechismInfo.objects.get_or_create(student=student)
            is_new = False
        except StudentProfile.DoesNotExist:
            student = None
            parent = None
            catechism = None
            is_new = True
        return student, parent, catechism, is_new

    def get(self, request):
        student, parent, catechism, is_new = self.get_student_objects(request)
        if not is_new and not student.is_pending:
            messages.warning(request, "Your profile has already been processed and cannot be edited.")
            return redirect("student_self:student_dashboard")

        context = {
            "student_form": StudentProfileForm(instance=student),
            "parent_form": ParentInfoForm(instance=parent),
            "catechism_form": CatechismInfoForm(instance=catechism),
            "is_new": is_new,
            "student": student,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        student, parent, catechism, is_new = self.get_student_objects(request)
        if not is_new and not student.is_pending:
            messages.warning(request, "Your profile has already been processed and cannot be edited.")
            return redirect("student_self:student_dashboard")

        student_form = StudentProfileForm(request.POST, instance=student)
        parent_form = ParentInfoForm(request.POST, instance=parent)
        catechism_form = CatechismInfoForm(request.POST, instance=catechism)

        if all([student_form.is_valid(), parent_form.is_valid(), catechism_form.is_valid()]):
            with transaction.atomic():
                student = student_form.save(commit=False)
                student.user = request.user
                student.status = 'pending'
                student.updated_by = request.user
                if is_new:
                    student.created_by = request.user
                student.save()
                
                parent = parent_form.save(commit=False)
                parent.student = student
                parent.save()
                
                catechism = catechism_form.save(commit=False)
                catechism.student = student
                catechism.save()

            if is_new:
                send_student_approval_request(student)
                messages.success(request, "Your profile has been submitted and is pending approval.")
            else:
                messages.success(request, "Your profile updates have been saved.")
                
            return redirect("student_self:student_dashboard")

        context = {
            "student_form": student_form,
            "parent_form": parent_form,
            "catechism_form": catechism_form,
            "is_new": is_new,
            "student": student,
        }
        return render(request, self.template_name, context)
