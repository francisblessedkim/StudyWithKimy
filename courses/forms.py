from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "start_date", "end_date", "thumbnail"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input"}),
            "description": forms.Textarea(attrs={"class": "input", "rows": 5}),
            "start_date": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "input"}),
        }
