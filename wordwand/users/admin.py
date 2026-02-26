from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, LoginActivity, AccountStatus


class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with additional display options"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'was_successful', 'login_time')
    list_filter = ('was_successful', 'login_time')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('login_time',)


@admin.register(AccountStatus)
class AccountStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__username',)
    readonly_fields = ('updated_at',)


# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
