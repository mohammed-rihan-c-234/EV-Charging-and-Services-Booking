from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re

from .models import Profile
from service_center.models import ServiceCenter


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, label="First name", required=False)
    phone_number = forms.CharField(max_length=30, label="Phone number", required=False)
    center_name = forms.CharField(max_length=200, label="Name of Center", required=False)
    center_phone = forms.CharField(max_length=30, label="Center Phone", required=False)
    center_address = forms.CharField(max_length=300, label="Center Address", required=False)
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        initial=Profile.ROLE_USER,
        widget=forms.RadioSelect,
        label="Account type",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("role", "full_name", "phone_number", "username", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        
        # Check if username contains only alphanumeric characters
        if not username.isalnum():
            raise forms.ValidationError("Username can only contain letters and numbers (no spaces or special characters).")
        
        # Check if username is only numbers
        if username.isdigit():
            raise forms.ValidationError("Username cannot be only numbers. Include at least one letter.")
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        
        return username

    def clean_full_name(self):
        value = (self.cleaned_data.get("full_name") or "").strip()
        role = (self.cleaned_data.get("role") or "").strip()
        if role != Profile.ROLE_SERVICE_CENTER:
            if not value:
                raise forms.ValidationError("First name is required.")
            if not value.replace(" ", "").isalpha():
                raise forms.ValidationError("First name can contain only alphabets and spaces.")
        return value

    def clean_phone_number(self):
        value = (self.cleaned_data.get("phone_number") or "").strip()
        role = (self.cleaned_data.get("role") or "").strip()
        if role != Profile.ROLE_SERVICE_CENTER:
            if not value:
                raise forms.ValidationError("Phone number is required.")
            if not value.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            if len(value) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        if role == Profile.ROLE_SERVICE_CENTER:
            center_name = (cleaned.get("center_name") or "").strip()
            center_phone = (cleaned.get("center_phone") or "").strip()
            center_address = (cleaned.get("center_address") or "").strip()
            if not center_name:
                self.add_error("center_name", "Center name is required.")
            if center_name and not center_name.replace(" ", "").isalpha():
                self.add_error("center_name", "Center name must contain only alphabets.")
            if not center_phone:
                self.add_error("center_phone", "Center phone is required.")
            if not center_address:
                self.add_error("center_address", "Center address is required.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile, _ = Profile.objects.update_or_create(
            user=user,
            defaults={
                "full_name": self.cleaned_data["full_name"].strip(),
                "phone_number": self.cleaned_data["phone_number"].strip(),
                "role": self.cleaned_data.get("role") or Profile.ROLE_USER,
            },
        )
        if profile.role == Profile.ROLE_SERVICE_CENTER:
            center_name = (self.cleaned_data.get("center_name") or "").strip()
            center_phone = (self.cleaned_data.get("center_phone") or "").strip()
            center_address = (self.cleaned_data.get("center_address") or "").strip()
            center = ServiceCenter.objects.create(
                name=center_name,
                phone=center_phone,
                address=center_address,
            )
            profile.full_name = center_name or user.username
            profile.phone_number = center_phone or profile.phone_number
            profile.service_center = center
            profile.save(update_fields=["service_center", "full_name", "phone_number"])
        return user


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("username", "email"):
            self.fields[name].widget.attrs.setdefault("class", "form-control")

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise forms.ValidationError("Username is required.")
        if not username.isalnum():
            raise forms.ValidationError("Username can only contain letters and numbers (no spaces or special characters).")
        if username.isdigit():
            raise forms.ValidationError("Username cannot be only numbers. Include at least one letter.")
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        return email


class ProfileEditForm(forms.ModelForm):
    center_name = forms.CharField(max_length=200, required=False, label="Name of Center")
    center_phone = forms.CharField(max_length=30, required=False, label="Center Phone")
    center_address = forms.CharField(max_length=300, required=False, label="Address")

    class Meta:
        model = Profile
        fields = ("full_name", "phone_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].widget.attrs.setdefault("class", "form-control")
        self.fields["phone_number"].widget.attrs.setdefault("class", "form-control")
        self.fields["center_name"].widget.attrs.setdefault("class", "form-control")
        self.fields["center_phone"].widget.attrs.setdefault("class", "form-control")
        self.fields["center_address"].widget.attrs.setdefault("class", "form-control")
        if self.instance and getattr(self.instance, "role", "") == Profile.ROLE_SERVICE_CENTER:
            center = getattr(self.instance, "service_center", None)
            if center:
                self.fields["center_name"].initial = center.name
                self.fields["center_phone"].initial = center.phone
                self.fields["center_address"].initial = center.address

    def clean_phone_number(self):
        value = (self.cleaned_data.get("phone_number") or "").strip()
        if self.instance and getattr(self.instance, "role", "") == Profile.ROLE_SERVICE_CENTER:
            return value
        if not value:
            raise forms.ValidationError("Phone number is required.")
        if not value.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(value) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def clean_full_name(self):
        value = (self.cleaned_data.get("full_name") or "").strip()
        if self.instance and getattr(self.instance, "role", "") == Profile.ROLE_SERVICE_CENTER:
            return value
        if not value:
            raise forms.ValidationError("Full name is required.")
        if not re.fullmatch(r"[A-Za-z ]+", value):
            raise forms.ValidationError("Full name can contain only alphabets and spaces.")
        return " ".join(value.split())

    def clean(self):
        cleaned = super().clean()
        if self.instance and getattr(self.instance, "role", "") == Profile.ROLE_SERVICE_CENTER:
            center_name = (cleaned.get("center_name") or "").strip()
            center_phone = (cleaned.get("center_phone") or "").strip()
            center_address = (cleaned.get("center_address") or "").strip()
            if not center_name:
                self.add_error("center_name", "Center name is required.")
            if center_name and not center_name.replace(" ", "").isalpha():
                self.add_error("center_name", "Center name must contain only alphabets.")
            if not center_phone:
                self.add_error("center_phone", "Center phone is required.")
            if not center_phone.isdigit():
                self.add_error("center_phone", "Center phone must contain only digits.")
            if center_phone and len(center_phone) != 10:
                self.add_error("center_phone", "Center phone must be exactly 10 digits.")
            if not center_address:
                self.add_error("center_address", "Address is required.")
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        if profile.role == Profile.ROLE_SERVICE_CENTER and profile.service_center:
            center = profile.service_center
            center.name = (self.cleaned_data.get("center_name") or center.name).strip()
            center.phone = (self.cleaned_data.get("center_phone") or center.phone).strip()
            center.address = (self.cleaned_data.get("center_address") or center.address).strip()
            if commit:
                center.save(update_fields=["name", "phone", "address"])
            profile.full_name = center.name
            profile.phone_number = center.phone
        if commit:
            profile.save()
        return profile
