from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    """Form for user registration with email"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name (Optional)'
    }))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name (Optional)'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        return email

    def clean_username(self):
        """Validate that username is unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.is_active = False  # Deactivate until email verification
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Form for user login"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

    class Meta:
        model = User
        fields = ('username', 'password')


class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_email(self):
        """Validate that email is unique (excluding current user)"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email address is already in use.')
        return email


class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address'
    }))

    def clean_email(self):
        """Validate that email exists in the system"""
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No account found with this email address.')
        return email


class PasswordResetForm(forms.Form):
    """Form for resetting password"""
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password'
    }), label='New Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }), label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Passwords do not match.')
            if len(password1) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
        return cleaned_data


class EmailVerificationForm(forms.Form):
    """Form for email verification"""
    code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter 6-digit code'
    }), label='Verification Code')
