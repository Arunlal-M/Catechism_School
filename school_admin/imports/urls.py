"""Import/Export URL routes."""

from django.urls import path

from . import views

app_name = "imports"

urlpatterns = [
    # Import flow
    path("upload/", views.ImportUploadView.as_view(), name="upload"),
    path("<int:batch_id>/mapping/", views.ColumnMappingView.as_view(), name="column_mapping"),
    path("<int:batch_id>/results/", views.ImportResultsView.as_view(), name="import_results"),
    path("<int:batch_id>/failed-rows/download/", views.DownloadFailedRowsView.as_view(), name="download_failed_rows"),
    path("history/", views.ImportHistoryView.as_view(), name="history"),

    # Export
    path("export/", views.ExportView.as_view(), name="export"),
]
