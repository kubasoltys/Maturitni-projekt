from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TrenerProfile, HracProfile, Trenink, DochazkaTreninky


#custom user model
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role a další', {'fields': ('role',)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role a další', {'fields': ('role',)}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')


# profil trenera
@admin.register(TrenerProfile)
class TrenerProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'club')


# profil hrace
@admin.register(HracProfile)
class HracProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'trener', 'cislo_dresu')


# trenink
@admin.register(Trenink)
class TreninkAdmin(admin.ModelAdmin):
    list_display = ('trener', 'datum', 'cas', 'typ')
    list_filter = ('typ', 'datum')


# dochazka
@admin.register(DochazkaTreninky)
class DochazkaTreninkyAdmin(admin.ModelAdmin):
    list_display = ('trenink', 'hrac', 'pritomen', 'hlasoval_v')
    list_filter = ('pritomen',)
