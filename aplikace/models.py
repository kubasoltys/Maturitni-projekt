from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


# profil trenera
class TrenerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=30,
                                  verbose_name='Jméno',
                                  blank=True,
                                  null=True)
    last_name = models.CharField(max_length=30,
                                 verbose_name='Příjmení')
    club = models.CharField(max_length=100,
                            verbose_name='Klub')

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Trenér - {self.club})"


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
        ('RW', 'Pravé křídlo'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trener = models.ForeignKey(TrenerProfile, on_delete=models.SET_NULL, null=True)

    first_name = models.CharField(max_length=30,
                                  verbose_name='Jméno',
                                  default='',
                                  blank=True)
    last_name = models.CharField(max_length=30,
                                 verbose_name='Příjmení')
    vek = models.PositiveIntegerField(validators=[MinValueValidator(5), MaxValueValidator(99)],
                                      verbose_name='Věk',
                                      default='18', )
    pozice = models.CharField(choices=POZICE_CHOICES,
                              verbose_name='Pozice',
                              default='—')
    cislo_dresu = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)],
                                              verbose_name='Číslo dresu',
                                              default='0')

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Hráč)"
