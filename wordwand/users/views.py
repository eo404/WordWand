from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from .forms import (
    UserRegisterForm, UserLoginForm, UserProfileUpdateForm,
    PasswordResetRequestForm, PasswordResetForm, EmailVerificationForm
)
import secrets
import string


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('child-home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            
            # Send verification email
            send_verification_email(request, user)
            
            messages.success(request, 
                f'Account created successfully! Please check your email ({email}) to verify your account.')
            return redirect('email-verify')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegisterForm()
    
    return render(request, 'user_authentication/register.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('child-home')
    
    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    # Redirect to next page or child home
                    next_url = request.GET.get('next', 'child-home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Your account is not active. Please verify your email.')
                    return redirect('email-verify')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid login credentials.')
    else:
        form = UserLoginForm()
    
    return render(request, 'user_authentication/login.html', {'form': form})


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def profile_view(request):
    """Display and update user profile"""
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'user_authentication/profile.html', context)


def email_verify_view(request):
    """Handle email verification page"""
    if request.user.is_authenticated and request.user.is_active:
        return redirect('child-home')
    
    form = EmailVerificationForm()
    context = {'form': form}
    return render(request, 'user_authentication/email_verify.html', context)


def password_reset_request_view(request):
    """Handle password reset request"""
    if request.user.is_authenticated:
        return redirect('child-home')
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)
            
            # Send password reset email
            send_password_reset_email(request, user)
            
            messages.success(request, 
                'Password reset link has been sent to your email. Please check your inbox.')
            return redirect('login')
        else:
            messages.error(request, 'An error occurred. Please try again.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'user_authentication/password_reset.html', {'form': form})


def password_reset_confirm_view(request, uidb64, token):
    """Handle password reset confirmation"""
    if request.user.is_authenticated:
        return redirect('child-home')
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    token_generator = PasswordResetTokenGenerator()
    
    if user is not None and token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get('password1')
                user.set_password(password)
                user.save()
                messages.success(request, 'Your password has been reset successfully. You can now login.')
                return redirect('login')
        else:
            form = PasswordResetForm()
        
        return render(request, 'user_authentication/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('login')


# Helper functions

def send_verification_email(request, user):
    """Send email verification link"""
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verify_url = request.build_absolute_uri(
        reverse('email-verify-confirm', kwargs={'uidb64': uid, 'token': token})
    )
    
    subject = 'Verify your WordWand account'
    html_message = render_to_string('user_authentication/email_verification_message.html', {
        'user': user,
        'verify_url': verify_url
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        'noreply@wordwand.com',
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(request, user):
    """Send password reset email"""
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    reset_url = request.build_absolute_uri(
        reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})
    )
    
    subject = 'Reset your WordWand password'
    html_message = render_to_string('user_authentication/password_reset_email.html', {
        'user': user,
        'reset_url': reset_url
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        'noreply@wordwand.com',
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def email_verify_confirm_view(request, uidb64, token):
    """Confirm email verification"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    token_generator = PasswordResetTokenGenerator()
    
    if user is not None:
        if user.is_active:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            next_url = request.GET.get('next')

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)

        return redirect('home')
