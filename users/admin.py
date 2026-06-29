from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from users.models import OTPVerification

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Info', {'fields': ('full_name',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Info', {'fields': ('full_name', 'email')}),
    )
    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'full_name')
    ordering = ('email',)

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at', 'is_verified')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__email', 'otp')
    readonly_fields = ('created_at',)

admin.site.register(User, CustomUserAdmin)
