from django import forms
from .models import TrenerProfile, HracProfile, Trenink, Zapas


# prihlaseni
class LoginForm(forms.Form):
    username = forms.CharField(
        label = 'Uživatelské jméno',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Zadejte uživatelské jméno',
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )
    password = forms.CharField(
        label = 'Heslo',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Zadejte heslo',
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )


# prvni prihlaseni trenera
class TrenerProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'placeholder': 'E-mail',
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )

    class Meta:
        model = TrenerProfile
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'club', 'club_photo','photo']
        labels = {
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'phone': 'Telefonní číslo',
            'birth_date': 'Datum narození',
            'club': 'Klub',
            'club_photo': 'Logo klubu',
            'photo': 'Fotografie',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Jméno',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Příjmení',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Telefonní číslo',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }, format='%Y-%m-%d'),
            'club': forms.TextInput(attrs={
                'placeholder': 'Klub',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'club_photo': forms.ClearableFileInput(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
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
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )

    trener = forms.ModelChoiceField(
        queryset=TrenerProfile.objects.all(),
        required=False,
        label="Vyberte trenéra",
        widget=forms.Select(attrs={
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )

    class Meta:
        model = HracProfile
        fields = [
            'first_name', 'last_name', 'email' , 'phone', 'birth_date', 'height', 'weight',
            'cislo_dresu', 'pozice', 'preferred_foot', 'trener', 'photo'
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
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Jméno',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Příjmení',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Telefonní číslo',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }, format='%Y-%m-%d'),
            'height': forms.NumberInput(attrs={
                'placeholder': 'Výška',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'weight': forms.NumberInput(attrs={
                'placeholder': 'Váha',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'cislo_dresu': forms.NumberInput(attrs={
                'placeholder': 'Číslo dresu',
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'pozice': forms.Select(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'preferred_foot': forms.Select(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
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



# trenink
class TreninkForm(forms.ModelForm):
    class Meta:
        model = Trenink
        fields = ['datum', 'cas', 'typ', 'poznamka']
        labels = {
            'datum': 'Datum',
            'cas': 'Čas',
            'typ': 'Typ tréninku',
            'poznamka': 'Poznámka',
        }
        widgets = {
            'datum': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'cas': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'typ': forms.Select(attrs={
                'placeholder': 'Vyber typ tréninku',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'poznamka': forms.Textarea(attrs={
                'placeholder': 'Poznámka (nepovinné)',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400',
                'rows': 3
            }),
        }



# zapas
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
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'datum': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'cas': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'domaci_hoste': forms.Select(attrs={
                'placeholder': 'Kdo je domácí a kdo host?',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'misto': forms.TextInput(attrs={
                'placeholder': 'Místo zápasu (např. domácí hřiště)',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
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
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'vysledek_soupere': forms.NumberInput(attrs={
                'placeholder': 'Góly soupeře',
                'class': 'w-full p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
        }