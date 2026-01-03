from django import forms
from .models import TrenerProfile, HracProfile, Trenink, Zapas, Tym


# prihlaseni
class LoginForm(forms.Form):
    username = forms.CharField(
        label='Uživatelské jméno',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Zadejte uživatelské jméno',
            'class': (
                'w-full p-4 border border-gray-300 rounded-2xl '
                'focus:outline-none focus:ring-2 focus:ring-green-700 '
                'transition-shadow shadow-sm focus:shadow-md'
            )
        })
    )

    password = forms.CharField(
        label='Heslo',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Zadejte heslo',
            'class': (
                'w-full p-4 border border-gray-300 rounded-2xl '
                'focus:outline-none focus:ring-2 focus:ring-green-700 '
                'transition-shadow shadow-sm focus:shadow-md'
            )
        })
    )



# prvni prihlaseni trenera
class TrenerProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-mail',
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
        })
    )

    class Meta:
        model = TrenerProfile
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'photo']
        labels = {
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'phone': 'Telefonní číslo',
            'birth_date': 'Datum narození',
            'photo': 'Fotografie',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Jméno',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Příjmení',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Telefonní číslo',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }, format='%Y-%m-%d'),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance').user if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
        if self.instance and self.instance.birth_date:
            self.fields['birth_date'].initial = self.instance.birth_date

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if hasattr(instance, 'user'):
                instance.user.email = self.cleaned_data.get('email', '')
                instance.user.save()
        return instance


# prvni prihlaseni hrace
class HracProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-mail',
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
        })
    )

    trener = forms.ModelChoiceField(
        queryset=TrenerProfile.objects.all(),
        required=False,
        label="Vyberte trenéra",
        widget=forms.Select(attrs={
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600',
            'id': 'id_trener'
        })
    )

    tym = forms.ModelChoiceField(
        queryset=Tym.objects.all(),
        required=False,
        label="Vyberte tým",
        widget=forms.Select(attrs={
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600',
            'id': 'id_tym'
        })
    )

    class Meta:
        model = HracProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'birth_date', 'height', 'weight',
            'cislo_dresu', 'pozice', 'preferred_foot', 'trener', 'tym', 'photo'
        ]
        labels = {
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'phone': 'Telefonní číslo',
            'birth_date': 'Datum narození',
            'height': 'Výška (cm)',
            'weight': 'Váha (kg)',
            'cislo_dresu': 'Číslo dresu',
            'pozice': 'Pozice',
            'preferred_foot': 'Preferovaná noha',
            'photo': 'Fotografie',
            'tym': 'Tým',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Jméno',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Příjmení',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Telefonní číslo',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }, format='%Y-%m-%d'),
            'height': forms.NumberInput(attrs={
                'placeholder': 'Výška',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'weight': forms.NumberInput(attrs={
                'placeholder': 'Váha',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'cislo_dresu': forms.NumberInput(attrs={
                'placeholder': 'Číslo dresu',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'pozice': forms.Select(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'preferred_foot': forms.Select(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance').user if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
        if self.instance and self.instance.birth_date:
            self.fields['birth_date'].initial = self.instance.birth_date
        
        if self.instance and self.instance.trener:
            self.fields['tym'].queryset = Tym.objects.filter(trener=self.instance.trener)
        elif args and args[0]:
            trener_id = args[0].get('trener')
            if trener_id:
                try:
                    trener = TrenerProfile.objects.get(pk=trener_id)
                    self.fields['tym'].queryset = Tym.objects.filter(trener=trener)
                except (TrenerProfile.DoesNotExist, ValueError):
                    self.fields['tym'].queryset = Tym.objects.none()
            else:
                self.fields['tym'].queryset = Tym.objects.none()
        else:
            self.fields['tym'].queryset = Tym.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if hasattr(instance, 'user'):
                instance.user.email = self.cleaned_data.get('email', '')
                instance.user.save()
        return instance


# ----------------------------------------------
# trenink
# ----------------------------------------------
class TreninkForm(forms.ModelForm):

    class Meta:
        model = Trenink
        fields = ['datum', 'cas', 'typ', 'poznamka']
        labels = {
            'datum': 'Datum',
            'cas': 'Čas',
            'typ': 'Typ tréninku',
            'poznamka': 'Poznámka'
        }
        widgets = {
            'datum': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'cas': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'typ': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'poznamka': forms.Textarea(attrs={
                'placeholder': 'Poznámka (nepovinné)',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600',
                'rows': 3
            }),
        }


# ----------------------------------------------
# zapas
# ----------------------------------------------
class ZapasForm(forms.ModelForm):

    class Meta:
        model = Zapas
        fields = ['souper', 'datum', 'cas', 'domaci_hoste', 'misto']
        labels = {
            'souper': 'Soupěř',
            'datum': 'Datum utkání',
            'cas': 'Čas utkání',
            'domaci_hoste': 'Váš tým je jako Domácí/Hosté',
            'misto': 'Místo konání',
        }
        widgets = {
            'souper': forms.TextInput(attrs={
                'placeholder': 'Zadej soupeře',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'datum': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'cas': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'domaci_hoste': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'misto': forms.TextInput(attrs={
                'placeholder': 'Místo zápasu (např. domácí hřiště)',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
        }


class DohranyZapasForm(forms.ModelForm):
    class Meta:
        model = Zapas
        fields = ['vysledek_tymu', 'vysledek_soupere']
        labels = {
            'vysledek_tymu': 'Výsledek týmu',
            'vysledek_soupere': 'Výsledek soupeře',
        }
        widgets = {
            'vysledek_tymu': forms.NumberInput(attrs={
                'placeholder': 'Góly tvého týmu',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
            'vysledek_soupere': forms.NumberInput(attrs={
                'placeholder': 'Góly soupeře',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-600'
            }),
        }
