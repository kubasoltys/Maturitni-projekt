from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TrenerProfile, HracProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Zobrazení v detailu uživatele
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role a další', {'fields': ('role',)}),
    )

    # Zobrazení při přidávání nového uživatele
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role a další', {'fields': ('role',)}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')


@admin.register(TrenerProfile)
class TrenerProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'club')


@admin.register(HracProfile)
class HracProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'trener', 'cislo_dresu')
