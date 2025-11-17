from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TrenerProfile, HracProfile, Tym, Trenink, DochazkaTreninky, Zapas, DochazkaZapasy, Gol, Karta


# -----------------------------
# custom user model
# -----------------------------
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


# -----------------------------
# tym
# -----------------------------
@admin.register(Tym)
class TymAdmin(admin.ModelAdmin):
    list_display = ('nazev', 'trener')
    search_fields = ('nazev',)


# -----------------------------
# trener
# -----------------------------
@admin.register(TrenerProfile)
class TrenerProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'seznam_tymu')

    def seznam_tymu(self, obj):
        tymy = obj.tymy.all()
        if not tymy:
            return "-"
        return ", ".join([t.nazev for t in tymy])
    seznam_tymu.short_description = "Týmy"


# -----------------------------
# hrac
# -----------------------------
@admin.register(HracProfile)
class HracProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'tym', 'cislo_dresu')
    list_filter = ('tym',)
    search_fields = ('user__first_name', 'user__last_name')


# -----------------------------
# trenink
# -----------------------------
@admin.register(Trenink)
class TreninkAdmin(admin.ModelAdmin):
    list_display = ('datum', 'cas', 'typ', 'tym')
    list_filter = ('typ', 'datum', 'tym')


# dochazka – treninky
@admin.register(DochazkaTreninky)
class DochazkaTreninkyAdmin(admin.ModelAdmin):
    list_display = ('trenink', 'hrac', 'pritomen', 'hlasoval_v')
    list_filter = ('pritomen', 'trenink__tym')


# -----------------------------
# zapasy
# -----------------------------
class GolInline(admin.TabularInline):
    model = Gol
    extra = 1


class KartaInline(admin.TabularInline):
    model = Karta
    extra = 1


@admin.register(Zapas)
class ZapasAdmin(admin.ModelAdmin):
    list_display = ('souper', 'datum', 'cas', 'misto', 'tym', 'pocet_golu', 'pocet_karet')
    list_filter = ('datum', 'tym')
    search_fields = ('souper', 'misto')
    inlines = [GolInline, KartaInline]

    def pocet_golu(self, obj):
        return obj.goly.count()
    pocet_golu.short_description = "Góly"

    def pocet_karet(self, obj):
        return obj.karty.count()
    pocet_karet.short_description = "Karty"


# dochazka – zapasy
@admin.register(DochazkaZapasy)
class DochazkaZapasyAdmin(admin.ModelAdmin):
    list_display = ('zapas', 'hrac', 'pritomen')
    list_filter = ('pritomen', 'zapas__tym')
