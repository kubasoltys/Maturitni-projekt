from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    ROLE = [
        ('hrac', 'Hráč'),
        ('trener', 'Trenér'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                verbose_name="Uživatel"
                                )
    role = models.CharField(max_length=10,
                            verbose_name="Role",
                            choices=ROLE,
                            default='hrac'
                            )

    def __str__(self):
        return f"{self.role}"