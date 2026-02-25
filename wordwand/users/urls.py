from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("email-verify/", views.email_verify_view, name="email-verify"),
    path("email-verify/<uidb64>/<token>/", views.email_verify_confirm_view, name="email-verify-confirm"),
    path("password-reset/", views.password_reset_request_view, name="password-reset"),
    path("password-reset/<uidb64>/<token>/", views.password_reset_confirm_view, name="password-reset-confirm"),
]
