from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для кастомного пользователя"""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('avatar', 'phone', 'country')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_blocked', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('email', 'phone', 'country', 'is_active', 'is_blocked', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_blocked', 'groups')
    search_fields = ('email', 'phone', 'country')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
