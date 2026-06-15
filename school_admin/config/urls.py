"""
Root URL Configuration — the main router.

HOW DJANGO URL ROUTING WORKS:
─────────────────────────────
1. A request comes in (e.g., GET /students/42/)
2. Django checks urlpatterns top-to-bottom
3. path("students/", include("students.urls")) matches "students/"
4. The remaining "42/" is passed to students/urls.py
5. path("<int:pk>/", ...) matches "42/" and calls StudentDetailView

include() delegates to each app's urls.py, keeping this file clean.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from accounts.views import LandingPageView
from students.views import AdminDashboardView
from students.urls import student_urlpatterns


urlpatterns = [
    # Root landing page
    path("", LandingPageView.as_view(), name="landing"),

    # Django admin (superuser only)
    path("admin/", admin.site.urls),

    # Auth
    path("accounts/", include("accounts.urls")),

    # Admin dashboard
    path("dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),

    # Student CRUD (admin-facing)
    path("students/", include("students.urls")),

    # Student self-service (student-facing)
    path("student/", include((student_urlpatterns, "students"), namespace="student_self")),

    # Master data management
    path("admissions/", include("admissions.urls")),

    # Import/Export
    path("imports/", include("imports.urls")),
]

# Serve media files in development (Django doesn't do this in production)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar URLs
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

# Customize Django admin header
admin.site.site_header = "Catechism 2025-2026"
admin.site.site_title = "Catechism 2025-2026 Portal"
admin.site.index_title = "Administration"
