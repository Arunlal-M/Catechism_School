"""
Master data views — manage Class, Division, Provision, Unit.

PATTERN: Generic CRUD with HTMX
────────────────────────────────
The master data page shows all 4 tables on one page.
Each table supports add/edit/delete via HTMX modals/partials.
This avoids full page reloads for simple operations.
"""

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from common.mixins import AdminRequiredMixin
from .forms import Division, Provision, SchoolClass, Unit, OccupationForm, DivisionForm, ProvisionForm, SchoolClassForm, UnitForm
from .models import Division, Provision, SchoolClass, Unit, Occupation


class MasterDataView(AdminRequiredMixin, View):
    """
    Main master data page — shows all lookup tables.
    """
    template_name = "admissions/master_data.html"

    def get(self, request):
        context = {
            "classes": SchoolClass.objects.all(),
            "divisions": Division.objects.all(),
            "occupations": Occupation.objects.all(),
            "provisions": Provision.objects.all(),
            "units": Unit.objects.select_related("provision").all(),
            "class_form": SchoolClassForm(),
            "division_form": DivisionForm(),
            "occupation_form": OccupationForm(),
            "provision_form": ProvisionForm(),
            "unit_form": UnitForm(),
        }
        return render(request, self.template_name, context)


class SchoolClassCreateView(AdminRequiredMixin, View):
    def post(self, request):
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class added successfully.")
        else:
            messages.error(request, "Error adding class. Check the form.")
        return redirect("admissions:master_data")


class SchoolClassDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(SchoolClass, pk=pk)
        try:
            obj.delete()
            messages.success(request, f"Class '{obj.name}' deleted.")
        except Exception:
            messages.error(request, "Cannot delete — this class has students assigned.")
        return redirect("admissions:master_data")


class DivisionCreateView(AdminRequiredMixin, View):
    def post(self, request):
        form = DivisionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Division added successfully.")
        else:
            messages.error(request, "Error adding division.")
        return redirect("admissions:master_data")


class DivisionDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(Division, pk=pk)
        try:
            obj.delete()
            messages.success(request, f"Division '{obj.name}' deleted.")
        except Exception:
            messages.error(request, "Cannot delete — this division has students assigned.")
        return redirect("admissions:master_data")


class OccupationCreateView(AdminRequiredMixin, View):
    def post(self, request):
        form = OccupationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Occupation added successfully.")
        else:
            messages.error(request, "Error adding occupation.")
        return redirect("admissions:master_data")


class OccupationDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(Occupation, pk=pk)
        try:
            obj.delete()
            messages.success(request, f"Occupation '{obj.name}' deleted.")
        except Exception:
            messages.error(request, "Cannot delete — this occupation has students assigned.")
        return redirect("admissions:master_data")


class ProvisionCreateView(AdminRequiredMixin, View):
    def post(self, request):
        form = ProvisionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Provision added successfully.")
        else:
            messages.error(request, "Error adding provision.")
        return redirect("admissions:master_data")


class ProvisionDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(Provision, pk=pk)
        try:
            obj.delete()
            messages.success(request, f"Provision '{obj.name}' deleted.")
        except Exception:
            messages.error(request, "Cannot delete — this provision has units or students.")
        return redirect("admissions:master_data")


class UnitCreateView(AdminRequiredMixin, View):
    def post(self, request):
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Unit added successfully.")
        else:
            messages.error(request, "Error adding unit.")
        return redirect("admissions:master_data")


class UnitDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        obj = get_object_or_404(Unit, pk=pk)
        try:
            obj.delete()
            messages.success(request, f"Unit '{obj.name}' deleted.")
        except Exception:
            messages.error(request, "Cannot delete — this unit has students assigned.")
        return redirect("admissions:master_data")


class UnitsForProvisionView(AdminRequiredMixin, View):
    """
    HTMX endpoint: returns <option> tags for units filtered by provision.

    Called when the user changes the Provision dropdown in the student form.
    Returns raw HTML (not a full page) that replaces the Unit <select> options.
    """
    def get(self, request):
        provision_id = request.GET.get("provision")
        if provision_id:
            units = Unit.objects.filter(provision_id=provision_id, is_active=True)
        else:
            units = Unit.objects.filter(is_active=True)

        html = '<option value="">---------</option>'
        for unit in units:
            html += f'<option value="{unit.pk}">{unit.name}</option>'
        return HttpResponse(html)
