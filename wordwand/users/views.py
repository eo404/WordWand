from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserRegisterForm, UserLoginForm, UserProfileUpdateForm


# ----------------------------
# Register View
# ----------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("profile")
    else:
        form = UserRegisterForm()

    return render(request, "user_authentication/register.html", {"form": form})


# ----------------------------
# Login View
# ----------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            next_url = request.POST.get("next") or request.GET.get("next") or "profile"
            return redirect(next_url)
    else:
        form = UserLoginForm()

    return render(request, "user_authentication/login.html", {"form": form})


# ----------------------------
# Logout View (POST only for CSRF safety)
# ----------------------------
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Logged out successfully.")
    return redirect("login")


# ----------------------------
# Profile View
# ----------------------------
@login_required
def profile_view(request):
    # Preserve the next URL across GET and POST
    next_url = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect(next_url) if next_url else redirect("profile")
    else:
        form = UserProfileUpdateForm(instance=request.user)

    return render(request, "user_authentication/profile.html", {
        "form": form,
        "next": next_url,
    })
