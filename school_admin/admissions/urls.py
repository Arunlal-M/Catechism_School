"""Admissions URL routes — master data management."""

from django.urls import path

from . import views

app_name = "admissions"

urlpatterns = [
    path("master-data/", views.MasterDataView.as_view(), name="master_data"),

    # Class CRUD
    path("classes/create/", views.SchoolClassCreateView.as_view(), name="class_create"),
    path("classes/<int:pk>/delete/", views.SchoolClassDeleteView.as_view(), name="class_delete"),

    # Division CRUD
    path("divisions/create/", views.DivisionCreateView.as_view(), name="division_create"),
    path("divisions/<int:pk>/delete/", views.DivisionDeleteView.as_view(), name="division_delete"),

    # Occupation CRUD
    path("occupations/create/", views.OccupationCreateView.as_view(), name="occupation_create"),
    path("occupations/<int:pk>/delete/", views.OccupationDeleteView.as_view(), name="occupation_delete"),

    # Provision CRUD
    path("provisions/create/", views.ProvisionCreateView.as_view(), name="provision_create"),
    path("provisions/<int:pk>/delete/", views.ProvisionDeleteView.as_view(), name="provision_delete"),

    # Unit CRUD
    path("units/create/", views.UnitCreateView.as_view(), name="unit_create"),
    path("units/<int:pk>/delete/", views.UnitDeleteView.as_view(), name="unit_delete"),

    # HTMX: dynamic unit filtering by provision
    path("units-for-provision/", views.UnitsForProvisionView.as_view(), name="units_for_provision"),
]
