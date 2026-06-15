"""
Authentication forms.

WHY CUSTOM FORMS?
─────────────────
Django provides AuthenticationForm, but it expects a 'username' field.
Since we use email login, we customize the form to show "Email" label
and use EmailInput widget for proper mobile keyboard support.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from common.constants import ROLE_ADMIN, ROLE_STUDENT
from .models import User


class EmailLoginForm(AuthenticationForm):
    """
    Login form using email instead of username.

    HOW IT WORKS:
    Django's AuthenticationForm uses 'username' internally. We don't
    change the field name (Django's auth backend expects it), but we
    change the label and widget so the user sees "Email".
    """
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Enter your email",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "placeholder": "Enter your password",
        }),
    )


class UserProfileForm(forms.ModelForm):
    """Form for users to edit their own profile (name, email)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
            }),
            "email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
            }),
        }


class CustomUserCreationForm(UserCreationForm):
    """Custom form for user registration."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name")
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
                "placeholder": "Enter your email",
            }),
            "first_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
                "placeholder": "First Name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
                "placeholder": "Last Name",
            }),
        }

    def __init__(self, *args, **kwargs):
        # Allow view to pass in a role, e.g. role='student' or role='admin'
        self.role = kwargs.pop('role', ROLE_STUDENT)
        super().__init__(*args, **kwargs)
        # Fix styling for built-in password fields
        for field in self.fields.values():
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.role
        if commit:
            user.save()
        return user
