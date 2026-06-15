"""Import forms."""

from django import forms


class ExcelUploadForm(forms.Form):
    """Form for uploading an Excel file."""
    file = forms.FileField(
        label="Excel File (.xlsx)",
        help_text="Upload an Excel file with student data.",
        widget=forms.FileInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500",
            "accept": ".xlsx,.xls",
        }),
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        if not uploaded_file.name.endswith((".xlsx", ".xls")):
            raise forms.ValidationError("Only Excel files (.xlsx, .xls) are supported.")
        # 10 MB limit
        if uploaded_file.size > 10 * 1024 * 1024:
            raise forms.ValidationError("File size must be under 10 MB.")
        return uploaded_file
