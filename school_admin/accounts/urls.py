"""Account URL routes."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("register/admin/", views.RegisterView.as_view(), {'role': 'admin'}, name="register_admin"),
    path("register/student/", views.RegisterView.as_view(), {'role': 'student'}, name="register_student"),
    
    # Admin Management
    path("admins/", views.AdminListView.as_view(), name="admin_list"),
    path("admins/create/", views.AdminCreateView.as_view(), name="admin_create"),
    path("admins/<int:pk>/edit/", views.AdminUpdateView.as_view(), name="admin_update"),
    path("admins/<int:pk>/delete/", views.AdminDeleteView.as_view(), name="admin_delete"),
    path("admins/<int:pk>/approve/", views.AdminApproveView.as_view(), name="admin_approve"),
]
