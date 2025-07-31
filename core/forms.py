from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class UploadFileForm(forms.Form):
    files = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        label="Select one or more files"
    )
