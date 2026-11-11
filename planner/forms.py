from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Task


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "due_date", "priority", "status")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "maxlength": 200}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        return title


class TaskFilterForm(forms.Form):
    """Reads the search/filter query string (GET). Invalid values are ignored."""

    q = forms.CharField(required=False, max_length=100)
    status = forms.ChoiceField(required=False, choices=[("", "All")] + Task.Status.choices)
    priority = forms.ChoiceField(required=False, choices=[("", "All")] + Task.Priority.choices)
    overdue = forms.BooleanField(required=False)
