# accounts/forms.py
from django import forms
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm, 
                                       PasswordResetForm, SetPasswordForm)
from .models import CustomUser

# Reusable Tailwind style
INPUT_CLASSES = "w-full px-4 py-2 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm transition-all"

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        
        self.fields['first_name'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Your First Name'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Your Last Name'
        })
        self.fields['email'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'you@example.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': INPUT_CLASSES,
            'placeholder': 'Confirm your password'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email



class LoginForm(AuthenticationForm):
    input_class = "w-full px-4 py-2 mt-2 border rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:bg-gray-900 dark:border-gray-700 dark:text-white"

    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "mr-2"})
    )

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Email',
            'class': self.input_class
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password',
            'class': self.input_class
        })


class PasswordResetForm(PasswordResetForm):
    input_class = "w-full px-4 py-2 mt-2 border rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:bg-gray-900 dark:border-gray-700 dark:text-white"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Enter your account email',
            'class': self.input_class
        })


class SetPasswordForm(SetPasswordForm):
    input_class = "w-full px-4 py-2 mt-2 border rounded-xl bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:bg-gray-900 dark:border-gray-700 dark:text-white"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'New password',
            'class': self.input_class
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Confirm new password',
            'class': self.input_class
        })
