"""
Student forms — create, edit, and student self-edit.

KEY DJANGO CONCEPT: ModelForm
─────────────────────────────
A ModelForm auto-generates form fields from a model's fields.
  - You list which fields to include
  - Validation from the model (validators, unique, required) is inherited
  - save() creates/updates the database record
  - You can add extra validation in clean() or clean_<fieldname>()

WHY THREE FORMS?
  1. StudentProfileForm — admin creates/edits all student fields
  2. ParentInfoForm — admin creates/edits parent details
  3. CatechismInfoForm — admin creates/edits catechism details

  These 3 forms are shown together on one page but saved separately.

WHY TAILWIND CLASSES IN WIDGETS?
  Django renders forms as plain HTML by default. Adding CSS classes to
  widgets lets us style them with Tailwind without writing custom templates
  for every single input field.
"""

from django import forms

from admissions.models import Unit
from common.validators import validate_not_future_date, validate_phone_number
from .models import CatechismInfo, ParentInfo, StudentProfile


# ──────────────────────────────────────────────
# Reusable widget CSS classes
# ──────────────────────────────────────────────
INPUT_CLASS = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
SELECT_CLASS = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white"
TEXTAREA_CLASS = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"


class StudentProfileForm(forms.ModelForm):
    """
    Form for creating/editing student records (admin use).
    """
    class Meta:
        model = StudentProfile
        fields = [
            "student_name", "email", "gender", "date_of_birth",
            "school_class", "division", "residential_address",
            "attended_catechism", "remarks",
        ]
        widgets = {
            "student_name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Full name"}),
            "email": forms.EmailInput(attrs={"class": INPUT_CLASS, "placeholder": "student@example.com"}),
            "gender": forms.Select(attrs={"class": SELECT_CLASS}),
            "date_of_birth": forms.DateInput(attrs={"class": INPUT_CLASS, "type": "date"}),
            "school_class": forms.Select(attrs={"class": SELECT_CLASS}),
            "division": forms.Select(attrs={"class": SELECT_CLASS}),
            "residential_address": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3}),
            "attended_catechism": forms.CheckboxInput(attrs={"class": "h-5 w-5 text-blue-600 rounded"}),
            "remarks": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3, "placeholder": "Optional notes..."}),
        }

    def clean_date_of_birth(self):
        """Extra validation on top of the model validator."""
        dob = self.cleaned_data.get("date_of_birth")
        if dob:
            validate_not_future_date(dob)
        return dob


class ParentInfoForm(forms.ModelForm):
    """Form for parent/guardian details."""
    class Meta:
        model = ParentInfo
        fields = [
            "father_name", "father_occupation", "father_phone",
            "mother_name", "mother_occupation", "mother_phone",
        ]
        widgets = {
            "father_name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Father's full name"}),
            "father_occupation": forms.Select(attrs={"class": SELECT_CLASS}),
            "father_phone": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "10-digit phone number"}),
            "mother_name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Mother's full name"}),
            "mother_occupation": forms.Select(attrs={"class": SELECT_CLASS}),
            "mother_phone": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "10-digit phone number"}),
        }

    def clean_father_phone(self):
        phone = self.cleaned_data.get("father_phone")
        if phone:
            validate_phone_number(phone)
        return phone

    def clean_mother_phone(self):
        phone = self.cleaned_data.get("mother_phone")
        if phone:
            validate_phone_number(phone)
        return phone


class CatechismInfoForm(forms.ModelForm):
    """
    Form for catechism-related details.

    DYNAMIC FILTERING: Unit dropdown is filtered by selected Provision.
    On initial load, we show all active units. HTMX will handle dynamic
    filtering when the user changes the Provision dropdown.
    """
    class Meta:
        model = CatechismInfo
        fields = ["catechism_teacher_name", "provision", "unit"]
        widgets = {
            "catechism_teacher_name": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Name of Catechism Teacher",
            }),
            "provision": forms.Select(attrs={
                "class": SELECT_CLASS,
                # HTMX: when provision changes, fetch filtered units
                "hx-get": "/admissions/units-for-provision/",
                "hx-target": "#id_unit",
                "hx-trigger": "change",
                "hx-swap": "innerHTML",
            }),
            "unit": forms.Select(attrs={"class": SELECT_CLASS, "id": "id_unit"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active provisions and units
        self.fields["provision"].queryset = self.fields["provision"].queryset.filter(is_active=True)
        self.fields["unit"].queryset = Unit.objects.filter(is_active=True)

        # If editing an existing record with a provision set, filter units
        if self.instance.pk and self.instance.provision_id:
            self.fields["unit"].queryset = Unit.objects.filter(
                provision=self.instance.provision, is_active=True,
            )


class StudentSelfEditForm(forms.ModelForm):
    """
    Limited form for students to edit their own record.
    Only allowed fields: address, email, remarks.
    """
    class Meta:
        model = StudentProfile
        fields = ["email", "residential_address", "remarks"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": INPUT_CLASS}),
            "residential_address": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3}),
            "remarks": forms.Textarea(attrs={"class": TEXTAREA_CLASS, "rows": 3}),
        }


class ParentPhoneEditForm(forms.ModelForm):
    """Limited form for students to update parent phone numbers."""
    class Meta:
        model = ParentInfo
        fields = ["father_phone", "mother_phone"]
        widgets = {
            "father_phone": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "mother_phone": forms.TextInput(attrs={"class": INPUT_CLASS}),
        }
