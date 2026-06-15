"""Forms for master data management."""

from django import forms

from .models import Division, Provision, SchoolClass, Unit, Occupation

INPUT_CLASS = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
SELECT_CLASS = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white"


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name", "order", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "e.g. Class 1"}),
            "order": forms.NumberInput(attrs={"class": INPUT_CLASS}),
            "is_active": forms.CheckboxInput(attrs={"class": "h-5 w-5 text-blue-600 rounded"}),
        }


class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ["name", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "e.g. A, B, C"}),
            "is_active": forms.CheckboxInput(attrs={"class": "h-5 w-5 text-blue-600 rounded"}),
        }


class OccupationForm(forms.ModelForm):
    class Meta:
        model = Occupation
        fields = ["name", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "e.g. Engineer, Doctor"}),
            "is_active": forms.CheckboxInput(attrs={"class": "h-5 w-5 text-blue-600 rounded"}),
        }


class ProvisionForm(forms.ModelForm):
    class Meta:
        model = Provision
        fields = ["name", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Pradeshikam name"}),
            "is_active": forms.CheckboxInput(attrs={"class": "h-5 w-5 text-blue-600 rounded"}),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["name", "provision", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Unit name"}),
            "provision": forms.Select(attrs={"class": SELECT_CLASS}),
            "is_active": forms.CheckboxInput(attrs={"class": "h-5 w-5 text-blue-600 rounded"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["provision"].queryset = Provision.objects.filter(is_active=True)
