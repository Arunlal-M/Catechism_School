"""Student URL routes — admin-facing."""

from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    # Admin CRUD
    path("", views.StudentListView.as_view(), name="student_list"),
    path("create/", views.StudentCreateView.as_view(), name="student_create"),
    path("<int:pk>/", views.StudentDetailView.as_view(), name="student_detail"),
    path("<int:pk>/edit/", views.StudentUpdateView.as_view(), name="student_update"),
    path("<int:pk>/delete/", views.StudentDeleteView.as_view(), name="student_delete"),
]

# Student self-service URLs (mounted at /student/ in root urls.py)
student_urlpatterns = [
    path("dashboard/", views.StudentDashboardView.as_view(), name="student_dashboard"),
    path("profile/form/", views.StudentSelfFormView.as_view(), name="student_self_form"),
]
