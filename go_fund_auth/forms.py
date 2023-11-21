from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

from django.core.exceptions import ValidationError
import re


def validate_egyptian_mobile(value):
    if not re.match(r'^(01)[0125][0-9]{8}$', value):
        raise ValidationError('Invalid Egyptian mobile phone number')


class CustomUserCreationForm(UserCreationForm):
    # Add style classes and attributes to the form inputs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

        self.fields['first_name'].widget.attrs['placeholder'] = 'first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'last name'
        self.fields['email'].widget.attrs['placeholder'] = 'simple@example.com'
        self.fields['password1'].widget.attrs['placeholder'] = 'Choose a strong password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
        self.fields['mobile_phone'].widget.attrs['placeholder'] = '01X XXXX XXXX'

    mobile_phone = forms.CharField(validators=[validate_egyptian_mobile])

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1',
                  'password2', 'mobile_phone', 'profile_picture']


class CustomUserChangeForm(forms.ModelForm):
    # Add style classes and attributes to the form inputs
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

        self.fields['first_name'].widget.attrs['placeholder'] = 'first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'last name'
        self.fields['mobile_phone'].widget.attrs['placeholder'] = '01X XXXX XXXX'
        self.fields['facebook_profile'].widget.attrs['placeholder'] = 'https://www.facebook.com/example'
        self.fields['country'].widget.attrs['placeholder'] = 'country'

    mobile_phone = forms.CharField(validators=[validate_egyptian_mobile])

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'mobile_phone',
                  'profile_picture', 'birthdate', 'facebook_profile', 'country']
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'}),
        label="Email Address"
    )