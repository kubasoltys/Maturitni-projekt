from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# profil trenera
class TrenerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=30,
                                  verbose_name='Jméno')
    last_name = models.CharField(max_length=30,
                                 verbose_name='Příjmení')
    club = models.CharField(max_length=100,
                                verbose_name='Klub',
                                default='Nezadán')

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Trenér - {self.club})"

# profil hrace
class HracProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    trener = models.ForeignKey(TrenerProfile, on_delete=models.SET_NULL, null=True)

    first_name = models.CharField(max_length=30,
                                  verbose_name='Jméno')
    last_name = models.CharField(max_length=30,
                                 verbose_name='Příjmení')

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Hráč)"