from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":3}))
    education = forms.CharField(required=False)
    skills = forms.CharField(required=False)
    portfolio_url = forms.URLField(required=False)
    resume = forms.FileField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=commit)
        Profile.objects.create(
            user=user,
            full_name=self.cleaned_data.get("full_name"),
            bio=self.cleaned_data.get("bio"),
            education=self.cleaned_data.get("education"),
            skills=self.cleaned_data.get("skills"),
            portfolio_url=self.cleaned_data.get("portfolio_url"),
            resume=self.cleaned_data.get("resume"),
        )
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "education", "skills", "portfolio_url", "resume"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "education": forms.TextInput(attrs={"class": "form-control"}),
            "skills": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "portfolio_url": forms.URLInput(attrs={"class": "form-control"}),
            "resume": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
