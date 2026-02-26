from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms


# ----------------------------
# Custom Register Form
# ----------------------------
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        ]


# ----------------------------
# Register View (No Email Verification)
# ----------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Direct activation
            user.save()

            # Auto login after register
            login(request, user)

            messages.success(request, "Account created successfully!")
            return redirect("profile")
    else:
        form = RegisterForm()

    return render(request, "user_authentication/register.html", {"form": form})


# ----------------------------
# Login View
# ----------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("profile")
    else:
        form = AuthenticationForm()

    return render(request, "user_authentication/login.html", {"form": form})


# ----------------------------
# Logout View
# ----------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


# ----------------------------
# Profile View
# ----------------------------
from .forms import UserProfileUpdateForm

@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = UserProfileUpdateForm(instance=request.user)

    return render(request, "user_authentication/profile.html", {"form": form})