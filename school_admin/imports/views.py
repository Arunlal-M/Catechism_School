"""
Import/Export views — upload, mapping, results, export downloads.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from common.mixins import AdminRequiredMixin
from students.filters import filter_students
from students.models import StudentProfile

from .exporters import export_failed_rows_excel, export_students_csv, export_students_excel
from .forms import ExcelUploadForm
from .models import AdmissionImportBatch
from .services import IMPORTABLE_FIELDS, auto_suggest_mapping, process_import, read_excel_headers


class ImportUploadView(AdminRequiredMixin, View):
    """
    Step 1: Upload an Excel file.

    On POST, saves the file and redirects to the column mapping page.
    """
    template_name = "imports/upload.html"

    def get(self, request):
        return render(request, self.template_name, {"form": ExcelUploadForm()})

    def post(self, request):
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]

            # Create the batch record with the uploaded file
            batch = AdmissionImportBatch.objects.create(
                uploaded_by=request.user,
                file_name=uploaded_file.name,
                file=uploaded_file,
            )
            return redirect("imports:column_mapping", batch_id=batch.pk)

        return render(request, self.template_name, {"form": form})


class ColumnMappingView(AdminRequiredMixin, View):
    """
    Step 2: Map Excel columns to database fields.

    Shows each Excel header and a dropdown of DB fields.
    Auto-suggests mappings where possible.
    """
    template_name = "imports/column_mapping.html"

    def get(self, request, batch_id):
        batch = get_object_or_404(AdmissionImportBatch, pk=batch_id)
        excel_headers = read_excel_headers(batch.file.path)
        suggestions = auto_suggest_mapping(excel_headers)

        context = {
            "batch": batch,
            "excel_headers": excel_headers,
            "db_fields": IMPORTABLE_FIELDS,
            "suggestions": suggestions,
        }
        return render(request, self.template_name, context)

    def post(self, request, batch_id):
        batch = get_object_or_404(AdmissionImportBatch, pk=batch_id)
        excel_headers = read_excel_headers(batch.file.path)

        # Build mapping from form: {"Excel Header": "db_field"}
        mapping = {}
        for header in excel_headers:
            db_field = request.POST.get(f"mapping_{header}")
            if db_field and db_field != "skip":
                mapping[header] = db_field

        # Check required fields are mapped
        required = {"student_name", "date_of_birth", "gender", "school_class", "division"}
        mapped_fields = set(mapping.values())
        missing = required - mapped_fields
        if missing:
            messages.error(
                request,
                f"Required fields not mapped: {', '.join(IMPORTABLE_FIELDS[f] for f in missing)}",
            )
            return redirect("imports:column_mapping", batch_id=batch.pk)

        # Save mapping and process
        batch.column_mapping = mapping
        batch.save()

        # Process the import
        process_import(batch.pk, request.user)

        messages.success(request, "Import completed! Review the results below.")
        return redirect("imports:import_results", batch_id=batch.pk)


class ImportResultsView(AdminRequiredMixin, DetailView):
    """Step 3: Show import results — success/fail/duplicate counts and row details."""
    model = AdmissionImportBatch
    template_name = "imports/import_results.html"
    context_object_name = "batch"
    pk_url_kwarg = "batch_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch = self.object
        context["success_rows"] = batch.rows.filter(status="success")[:20]
        context["failed_rows"] = batch.rows.filter(status="failed")
        context["duplicate_rows"] = batch.rows.filter(status="duplicate")
        return context


class ImportHistoryView(AdminRequiredMixin, ListView):
    """List of all past import batches."""
    model = AdmissionImportBatch
    template_name = "imports/batch_history.html"
    context_object_name = "batches"
    paginate_by = 20


class DownloadFailedRowsView(AdminRequiredMixin, View):
    """Download failed rows as Excel for fixing and re-uploading."""
    def get(self, request, batch_id):
        batch = get_object_or_404(AdmissionImportBatch, pk=batch_id)
        return export_failed_rows_excel(batch)


class ExportView(AdminRequiredMixin, View):
    """Export filtered student data as CSV or Excel."""
    template_name = "imports/export.html"

    def get(self, request):
        # Show export page with current filter summary
        from admissions.models import Division, Provision, SchoolClass
        from common.constants import GENDER_CHOICES, STATUS_CHOICES

        context = {
            "classes": SchoolClass.objects.filter(is_active=True),
            "divisions": Division.objects.filter(is_active=True),
            "provisions": Provision.objects.filter(is_active=True),
            "status_choices": STATUS_CHOICES,
            "gender_choices": GENDER_CHOICES,
            "current_filters": request.GET,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Generate and download the export file."""
        # Apply same filters as student list
        queryset = filter_students(StudentProfile.objects.all(), request.POST)

        export_format = request.POST.get("format", "csv")
        if export_format == "excel":
            return export_students_excel(queryset)
        return export_students_csv(queryset)
