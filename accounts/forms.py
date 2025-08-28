# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

def _user_has_field(name: str) -> bool:
    return any(f.name == name for f in User._meta.get_fields())

class SignupForm(UserCreationForm):
    # Use role choices from the model if present; fallback safely
    try:
        ROLE_CHOICES = User._meta.get_field("role").choices
    except Exception:
        ROLE_CHOICES = (("student", "Student"), ("teacher", "Teacher"))

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional photo field (don’t mutate Meta.fields)
        if _user_has_field("photo"):
            self.fields["photo"] = forms.ImageField(required=False)

        # Tailwind classes
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "input")
        self.fields["password1"].widget.attrs["class"] = "input"
        self.fields["password2"].widget.attrs["class"] = "input"

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        """Persist optional photo too."""
        user = super().save(commit=False)
        if "photo" in self.fields:
            user.photo = self.cleaned_data.get("photo") or getattr(user, "photo", None)
        if commit:
            user.save()
        return user
