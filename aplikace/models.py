from datetime import date
#from tabnanny import verbose
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone


# custom user model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('hrac', 'Hráč'),
        ('trener', 'Trenér'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='hrac')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"



# profil trenera
class TrenerProfile(models.Model):
    user = models.OneToOneField(
        'aplikace.User',
        related_name='trenerprofile',
        on_delete=models.CASCADE)
    first_name = models.CharField(
        max_length=30,
        verbose_name='Jméno',
        blank=True,
        null=True)
    last_name = models.CharField(
        max_length=30,
        verbose_name='Příjmení',
        blank=True,
        null=True)
    phone = models.CharField(
        max_length=10,
        verbose_name='Telefonní číslo',
        blank=True,
        null=True)
    birth_date = models.DateField(
        verbose_name='Datum narození',
        blank=True,
        null=True)
    club = models.CharField(
        max_length=100,
        verbose_name='Klub')
    club_photo = models.ImageField(
        upload_to='klub_photo/',
        verbose_name='Logo klubu',
        blank=True,
        null=True)
    photo = models.ImageField(
        upload_to='trener_photo/',
        verbose_name='Fotografie',
        blank=True,
        null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# vypocet veku
    @property
    def vek(self):
        if not self.birth_date:
            return "Neuvedeno"
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

# overeni at je zadano aspon jmeno nebo prijmeni
    def clean(self):
        super().clean()
        if not (self.first_name or self.last_name):
            raise ValidationError("Musíte zadat alespoň jméno nebo příjmení.")

# nastaveni zobrazeni trenera
    def __str__(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"{full_name} ({self.club})"

    class Meta:
        verbose_name = "Trenér"
        verbose_name_plural = "Trenéři"
        ordering = ['last_name', 'first_name']



# profil hrace
class HracProfile(models.Model):
    POZICE_CHOICES = [
        ('GK', 'Brankář'),
        ('DF', 'Obránce'),
        ('CB', 'Střední obránce'),
        ('LB', 'Levý obránce'),
        ('RB', 'Pravý obránce'),
        ('LWB', 'Levý ofenzivní obránce'),
        ('RWB', 'Pravý ofenzivní obránce'),
        ('MF', 'Záložník'),
        ('CM', 'Střední záložník'),
        ('LM', 'Levý záložník'),
        ('RM', 'Pravý záložník'),
        ('AM', 'Ofenzivní záložník'),
        ('FW', 'Útočník'),
        ('CF', 'Střední útočník'),
        ('ST', 'Hrotový útočník'),
        ('LW', 'Levé křídlo'),
        ('RW', 'Pravé křídlo'),]
    user = models.OneToOneField(
        'aplikace.User',
        related_name='hracprofile',
        on_delete=models.CASCADE)
    trener = models.ForeignKey(
        'TrenerProfile',
        related_name='hrac',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    first_name = models.CharField(
        max_length=30,
        verbose_name='Jméno',
        blank=True,
        null=True)
    last_name = models.CharField(
        max_length=30,
        verbose_name='Příjmení',
        blank=True,
        null=True)
    phone = models.CharField(
        max_length=10,
        verbose_name='Telefonní číslo',
        blank=True,
        null=True)
    birth_date = models.DateField(
        verbose_name='Datum narození',
        blank=True,
        null=True)
    height = models.PositiveIntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        verbose_name='Výška (cm)',
        blank=True,
        null=True)
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(150)],
        verbose_name='Váha (kg)',
        blank=True,
        null=True)
    cislo_dresu = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        verbose_name='Číslo dresu',
        blank=True,
        null=True)
    pozice = models.CharField(
        choices=POZICE_CHOICES,
        verbose_name='Pozice',
        blank=True,
        null=True)
    preferred_foot = models.CharField(
        max_length=15,
        choices=[('Levá', 'Levá noha'), ('Pravá', 'Pravá noha')],
        verbose_name='Preferovaná noha',
        blank=True,
        null=True)
    photo = models.ImageField(
        upload_to='hrac_photo/',
        verbose_name='Fotografie',
        blank=True,
        null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#vypocet veku
    @property
    def vek(self):
        if not self.birth_date:
            return "-"
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

# overeni at je zadano aspon jmeno nebo prijmeni
    def clean(self):
        super().clean()
        if not (self.first_name or self.last_name):
            raise ValidationError("Musíte zadat alespoň jméno nebo příjmení.")

# nastaveni zobrazeni hrace
    def __str__(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"{full_name} (Hráč)"

    class Meta:
        verbose_name = "Hráč"
        verbose_name_plural = "Hráči"
        ordering = ['last_name', 'first_name']



#treninky
class Trenink(models.Model):
    STAVY = [
        ('Naplánováno', 'Naplánováno'),
        ('Dokončeno', 'Dokončeno'),
    ]

    TYPY = [
        ('Fyzická příprava', 'Fyzická příprava'),
        ('Taktická připrava', 'Taktická příprava'),
        ('Jiný', 'Jiné'),
    ]

    trener = models.ForeignKey(
        'TrenerProfile',
        on_delete=models.CASCADE,
        related_name='treninky'
    )
    datum = models.DateField(
        verbose_name='Datum'
    )
    cas = models.TimeField(
        verbose_name='Cas'
    )
    typ = models.CharField(
        max_length=20,
        choices=TYPY,
        verbose_name='Typ tréninku'
    )
    poznamka = models.TextField(
        verbose_name='Poznámka',
        blank=True,
        null=True
    )
    stav = models.CharField(
        max_length=20,
        choices=STAVY,
        default='Naplánováno',
        verbose_name="Stav tréninku"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-datum', '-cas']
        verbose_name = "Trénink"
        verbose_name_plural = "Tréninky"

    def __str__(self):
        return f"{self.get_typ_display()} — {self.datum} {self.cas.strftime('%H:%M')} ({self.trener})"

    def dochazka_summary(self):
        total = self.dochazka.count()
        ano = self.dochazka.filter(pritomen=True).count()
        ne = self.dochazka.filter(pritomen=False).count()
        nehlasoval = self.dochazka.filter(pritomen__isnull=True).count()
        return {'total': total, 'ano': ano, 'ne': ne, 'nehlasoval': nehlasoval}



# dochazka na treninky
class DochazkaTreninky(models.Model):
    trenink = models.ForeignKey(
        Trenink,
        on_delete=models.CASCADE,
        related_name='dochazka'
    )
    hrac = models.ForeignKey(
        'HracProfile',
        on_delete=models.CASCADE,
        related_name='dochazka'
    )
    pritomen = models.BooleanField(null=True, blank=True, default=None)
    duvod = models.CharField(max_length=250, blank=True, null=True)
    hlasoval_v = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['trenink', 'hrac'], name='unique_trenink_hrac')
        ]
        verbose_name = "Docházka na trénink"
        verbose_name_plural = "Docházky na tréninky"


    def __str__(self):
        status = 'ANO' if self.pritomen is True else ('NE' if self.pritomen is False else 'NEHLASOVAL')
        return f"{self.hrac} — {self.trenink} ({status})"



# zapasy
class Zapas(models.Model):
    STAVY = [
        ('Naplánováno', 'Naplánováno'),
        ('Dohráno', 'Dohráno'),
    ]

    DOMACI_HOSTE = [
        ('Domácí', 'Domácí'),
        ('Hosté', 'Hosté'),
    ]

    trener = models.ForeignKey(
        "TrenerProfile",
        on_delete=models.CASCADE,
        related_name="zapasy"
    )
    club = models.CharField(
        max_length=100,
        verbose_name="Tým",
        blank=True
    )
    souper = models.CharField(
        max_length=100,
        verbose_name="Soupěř",
    )
    datum = models.DateField(
        default=timezone.now,
        verbose_name='Datum'
    )
    cas = models.TimeField(
        verbose_name='Čas',
        null=True,
        blank=True
    )
    domaci_hoste = models.CharField(
        max_length=10,
        choices=DOMACI_HOSTE,
        default='Domácí',
        verbose_name='Domácí/Hosté'
    )
    misto = models.CharField(
        verbose_name='Místo',
        max_length=150,
        blank=True
    )
    popis = models.TextField(
        verbose_name='Popis',
        blank=True
    )
    stav = models.CharField(
        max_length=20,
        choices=STAVY,
        default='Naplánováno',
        verbose_name="Stav zápasu"
    )
    vysledek_tymu = models.PositiveSmallIntegerField(
        verbose_name='Výsledek týmu',
        null=True,
        blank=True
    )
    vysledek_soupere = models.PositiveSmallIntegerField(
        verbose_name='Výsledek soupeře',
        null=True,
        blank=True
    )
    dokonceno_dne = models.DateTimeField(
        verbose_name="Dokončeno dne",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['datum', 'cas']
        verbose_name = "Zápas"
        verbose_name_plural = "Zápasy"

    def __str__(self):
        return f"{self.souper} ({self.datum})"

    @property
    def je_dokonceny(self):
        return self.stav == 'dokonceny'



# dochazka na zapasy
class DochazkaZapasy(models.Model):
    zapas = models.ForeignKey(
        Zapas,
        on_delete=models.CASCADE,
        related_name="dochazka"
    )
    hrac = models.ForeignKey(
        "HracProfile",
        on_delete=models.CASCADE
    )
    pritomen = models.BooleanField(
        verbose_name="Přítomen",
        null=True,
        blank=True
    )
    poznamka = models.CharField(
        max_length=255,
        verbose_name="Poznámka",
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ("zapas", "hrac")
        verbose_name = "Docházka na zápas"
        verbose_name_plural = "Docházky na zápasy"

    def __str__(self):
        stav = "✅" if self.pritomen else ("❌" if self.pritomen is False else "⏳")
        return f"{self.hrac} - {self.zapas} ({stav})"