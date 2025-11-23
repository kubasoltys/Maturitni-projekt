from datetime import date, datetime
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# custom user model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('hrac', 'Hráč'),
        ('trener', 'Trenér'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='hrac')

    first_login = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"



#-----------------------------------------------------------------------------------
# PROFILY
#-----------------------------------------------------------------------------------


# trener
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
    photo = models.ImageField(
        upload_to='trener_photo/',
        verbose_name='Fotografie',
        blank=True,
        null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def vek(self):
        if not self.birth_date:
            return "Neuvedeno"
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def clean(self):
        super().clean()
        if not (self.first_name or self.last_name):
            raise ValidationError("Musíte zadat alespoň jméno nebo příjmení.")

    def __str__(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"{full_name}"

    class Meta:
        verbose_name = "Trenér"
        verbose_name_plural = "Trenéři"
        ordering = ['last_name', 'first_name']



#-----------------------------------------------------------------------------------
# TYM
#-----------------------------------------------------------------------------------
class Tym(models.Model):
    KATEGORIE = [
        ('U6-U9', 'U6-U9'),
        ('U10-U11', 'U10-U11'),
        ('U12-U13', 'U12-U13'),
        ('U14-U15', 'U14-U15'),
        ('U16-U19', 'U16-U19'),
        ('Muži', 'Muži'),
        ('Ženy', 'Ženy'),
    ]

    nazev = models.CharField(
        max_length=100,
        verbose_name="Název týmu")
    kategorie = models.CharField(
        max_length=50,
        choices=KATEGORIE,
        blank=True,
        null=True)
    trener = models.ForeignKey(
        TrenerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tymy")
    stadion = models.CharField(
        max_length=150,
        verbose_name="Stadion",
        blank=True,
        null=True)
    mesto = models.CharField(
        max_length=100,
        verbose_name="Město",
        blank=True,
        null=True)
    logo = models.ImageField(
        upload_to="klub_photo/",
        blank=True,
        null=True)

    def __str__(self):
        return f"{self.nazev} ({self.kategorie})" if self.kategorie else self.nazev

    class Meta:
        verbose_name = "Tým"
        verbose_name_plural = "Týmy"
        ordering = ['nazev']




# hrac
class HracProfile(models.Model):
    POZICE = [
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

    NOHA = [('Levá', 'Levá noha'),
            ('Pravá', 'Pravá noha')]

    user = models.OneToOneField(
        'aplikace.User',
        related_name='hracprofile',
        on_delete=models.CASCADE)
    trener = models.ForeignKey(
        'TrenerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hraci")
    tym = models.ForeignKey(
        Tym,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hraci")
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
        validators=[MinValueValidator(100),
                    MaxValueValidator(250)],
        verbose_name='Výška (cm)',
        blank=True,
        null=True)
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(30),
                    MaxValueValidator(150)],
        verbose_name='Váha (kg)',
        blank=True,
        null=True)
    cislo_dresu = models.PositiveIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(99)],
        verbose_name='Číslo dresu',
        blank=True,
        null=True)
    pozice = models.CharField(
        max_length=5,
        choices=POZICE,
        verbose_name='Pozice',
        blank=True,
        null=True)
    preferred_foot = models.CharField(
        max_length=15,
        choices=NOHA,
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


    # pocitani dochazky na treninky v %
    def _trenink_stats(self):
        now = timezone.now()

        tymy_hrace = [self.tym] if self.tym else []

        treninky = Trenink.objects.filter(tym__in=tymy_hrace)
        probehle = []

        for trenink in treninky:
            trenink_datetime = timezone.make_aware(
                datetime.combine(trenink.datum, trenink.cas),
                timezone.get_current_timezone()
            )

            if trenink_datetime < now:
                trenink.doplnit_nehlasujici_hrace()
                probehle.append(trenink)

        if not probehle:
            return 0, 0

        pritomni = 0
        for trenink in probehle:
            doch = trenink.dochazka.filter(hrac=self).first()
            if doch and doch.pritomen:
                pritomni += 1

        return pritomni, len(probehle)

    @property
    def dochazka_treninky(self):
        pritomni, celkem = self._trenink_stats()
        if celkem == 0:
            return 0
        return round(pritomni / celkem * 100)

    @property
    def treninky_pritomen(self):
        return self._trenink_stats()[0]

    @property
    def treninky_nepritomen(self):
        pritomni, celkem = self._trenink_stats()
        return celkem - pritomni


    # pocitani dochazky na zapasy v %
    def _zapas_stats(self):
        now = timezone.now()

        tymy_hrace = [self.tym] if self.tym else []

        zapasy = Zapas.objects.filter(tym__in=tymy_hrace)
        probehle = []

        for zapas in zapasy:
            zapas_datetime = timezone.make_aware(
                datetime.combine(zapas.datum, zapas.cas),
                timezone.get_current_timezone()
            )

            if zapas_datetime < now:
                if hasattr(zapas, "doplnit_nehlasujici_hrace"):
                    zapas.doplnit_nehlasujici_hrace()

                probehle.append(zapas)

        if not probehle:
            return 0, 0

        pritomni = 0
        for zapas in probehle:
            doch = zapas.dochazka.filter(hrac=self).first()
            if doch and doch.pritomen:
                pritomni += 1

        return pritomni, len(probehle)

    @property
    def dochazka_zapasy(self):
        pritomni, celkem = self._zapas_stats()
        if celkem == 0:
            return 0
        return round((pritomni / celkem) * 100)

    @property
    def zapasy_pritomen(self):
        return self._zapas_stats()[0]

    @property
    def zapasy_nepritomen(self):
        pritomni, celkem = self._zapas_stats()
        return celkem - pritomni


    def save(self, *args, **kwargs):
        if self.trener and not self.tym:
            tymy_trenera = Tym.objects.filter(trener=self.trener)
            if tymy_trenera.exists():
                self.tym = tymy_trenera.first()
        super().save(*args, **kwargs)


    @property
    def vek(self):
        if not self.birth_date:
            return "-"
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))


    def clean(self):
        super().clean()
        if not (self.first_name or self.last_name):
            raise ValidationError("Musíte zadat alespoň jméno nebo příjmení.")


    def __str__(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"{full_name} (Hráč)"


    class Meta:
        verbose_name = "Hráč"
        verbose_name_plural = "Hráči"
        ordering = ['last_name', 'first_name']



#-----------------------------------------------------------------------------------
# TRENINKY
#-----------------------------------------------------------------------------------


# treninky
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

    tym = models.ForeignKey(
        'Tym',
        on_delete=models.CASCADE,
        related_name='treninky',
        null=True,
        blank=True)
    datum = models.DateField(
        default=timezone.now,
        verbose_name='Datum')
    cas = models.TimeField(
        verbose_name='Čas')
    typ = models.CharField(
        max_length=20,
        choices=TYPY,
        verbose_name='Typ tréninku')
    poznamka = models.TextField(
        verbose_name='Poznámka',
        blank=True,
        null=True)
    stav = models.CharField(
        max_length=20,
        choices=STAVY,
        default='Naplánováno',
        verbose_name="Stav tréninku")

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-datum', '-cas']
        verbose_name = "Trénink"
        verbose_name_plural = "Tréninky"

    def __str__(self):
        return f"{self.get_typ_display()} — {self.datum} {self.cas.strftime('%H:%M')} ({self.tym})"

    def dochazka_summary(self):
        total = self.dochazka.count()
        ano = self.dochazka.filter(pritomen=True).count()
        ne = self.dochazka.filter(pritomen=False).count()
        nehlasoval = self.dochazka.filter(pritomen__isnull=True).count()
        return {'total': total, 'ano': ano, 'ne': ne, 'nehlasoval': nehlasoval}

    def doplnit_nehlasujici_hrace(self):
        if not self.tym:
            return

        hraci = self.tym.hraci.all()
        for hrac in hraci:
            if not self.dochazka.filter(hrac=hrac).exists():
                DochazkaTreninky.objects.create(
                    trenink=self,
                    hrac=hrac,
                    pritomen=False,
                    duvod=None
                )


# dochazka na treninky
class DochazkaTreninky(models.Model):
    trenink = models.ForeignKey(
        Trenink,
        on_delete=models.CASCADE,
        related_name='dochazka')
    hrac = models.ForeignKey(
        'HracProfile',
        on_delete=models.CASCADE,
        related_name='dochazka')
    pritomen = models.BooleanField(
        null=True,
        blank=True,
        default=None)
    duvod = models.CharField(
        max_length=250,
        blank=True,
        null=True)
    hlasoval_v = models.DateTimeField(
        auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['trenink', 'hrac'], name='unique_trenink_hrac')
        ]
        verbose_name = "Docházka na trénink"
        verbose_name_plural = "Docházky na tréninky"

    def __str__(self):
        status = 'ANO' if self.pritomen is True else ('NE' if self.pritomen is False else 'NEHLASOVAL')
        return f"{self.hrac} — {self.trenink} ({status})"



#-----------------------------------------------------------------------------------
# ZAPASY
#-----------------------------------------------------------------------------------


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

    tym = models.ForeignKey(
        'Tym',
        on_delete=models.CASCADE,
        related_name='zapasy',
        null=True,
        blank=True)
    souper = models.CharField(
        max_length=100,
        verbose_name="Soupěř")
    datum = models.DateField(
        default=timezone.now,
        verbose_name='Datum')
    cas = models.TimeField(
        verbose_name='Čas',
        null=True,
        blank=True)
    domaci_hoste = models.CharField(
        max_length=10,
        choices=DOMACI_HOSTE,
        default='Domácí',
        verbose_name='Domácí/Hosté')
    misto = models.CharField(
        verbose_name='Místo',
        max_length=150,
        blank=True)
    stav = models.CharField(
        max_length=20,
        choices=STAVY,
        default='Naplánováno',
        verbose_name="Stav zápasu")
    vysledek_tymu = models.PositiveSmallIntegerField(
        verbose_name='Výsledek týmu',
        null=True,
        blank=True)
    vysledek_soupere = models.PositiveSmallIntegerField(
        verbose_name='Výsledek soupeře',
        default=0)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['datum', 'cas']
        verbose_name = "Zápas"
        verbose_name_plural = "Zápasy"

    def __str__(self):
        return f"{self.souper} ({self.datum})"

    @property
    def je_dokonceny(self):
        return self.stav == 'Dohráno'


# dochazka na zapasy
class DochazkaZapasy(models.Model):
    zapas = models.ForeignKey(
        Zapas,
        on_delete=models.CASCADE,
        related_name="dochazka")
    hrac = models.ForeignKey(
        'HracProfile',
        on_delete=models.CASCADE)
    pritomen = models.BooleanField(
        verbose_name="Přítomen",
        null=True,
        blank=True)
    poznamka = models.CharField(
        max_length=255,
        verbose_name="Poznámka",
        blank=True,
        null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["zapas", "hrac"],
                name="unique_zapas_hrac"
            )
        ]
        verbose_name = "Docházka na zápas"
        verbose_name_plural = "Docházky na zápasy"

    def __str__(self):
        stav = "ANO" if self.pritomen else ("NE" if self.pritomen is False else "NEHLASOVAL")
        return f"{self.hrac} - {self.zapas} ({stav})"



#-----------------------------------------------------------------------------------
# STATISTIKY
#-----------------------------------------------------------------------------------


# goly
class Gol(models.Model):
    TYP_GOLU = [
        ('normalni', 'Normální'),
        ('penalta', 'Penalta'),
        ('primak', 'Přímý kop'),
        ('vlastni', 'Vlastní gól'),
    ]

    zapas = models.ForeignKey(
        Zapas,
        on_delete=models.CASCADE,
        related_name="goly")
    hrac = models.ForeignKey(
        HracProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goly")
    minuta = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(140)],
        verbose_name="Minuta")
    typ = models.CharField(
        max_length=20,
        choices=TYP_GOLU)


    def __str__(self):
        hrac = self.hrac or "Neznámý hráč"
        return f"Gól: {hrac} — {self.zapas} ({self.get_typ_display()} | {self.minuta}. min)"

    class Meta:
        verbose_name = "Gól"
        verbose_name_plural = "Góly"
        ordering = ['minuta']



# karty
class Karta(models.Model):
    TYP_KARTY = [
        ('zluta', 'Žlutá'),
        ('cervena', 'Červená'),
    ]

    zapas = models.ForeignKey(
        Zapas,
        on_delete=models.CASCADE,
        related_name="karty")
    hrac = models.ForeignKey(
        HracProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="karty")
    typ = models.CharField(
        max_length=10,
        choices=TYP_KARTY)
    minuta = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),
                    MaxValueValidator(140)],
        verbose_name="Minuta")


    def __str__(self):
        hrac = self.hrac or "Neznámý hráč"
        return f"Karta: {hrac} — {self.zapas} ({self.get_typ_display()} | {self.minuta}. min)"

    class Meta:
        verbose_name = "Karta"
        verbose_name_plural = "Karty"
        ordering = ['minuta']

