from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


# profil trenera
class TrenerProfile(models.Model):
    user = models.OneToOneField(
        User,
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
        verbose_name='Datum narození')
    club = models.CharField(
        max_length=100,
        verbose_name='Klub')
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
        return f"{full_name} (Trenér - {self.club})"

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
        User,
        related_name='hracprofile',
        on_delete=models.CASCADE)
    trener = models.ForeignKey(
        TrenerProfile,
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
        verbose_name='Datum narození')
    height = models.PositiveIntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        verbose_name='Výška (cm)')
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(150)],
        verbose_name='Váha (kg)')
    cislo_dresu = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        verbose_name='Číslo dresu',
        default=0)
    pozice = models.CharField(
        choices=POZICE_CHOICES,
        verbose_name='Pozice',
        default='ST')
    preferred_foot = models.CharField(
        max_length=15,
        choices=[('left', 'Levá noha'), ('right', 'Pravá noha'), ('both', 'Obě nohy')],
        verbose_name='Preferovaná noha',
        default='right')
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