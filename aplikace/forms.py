from django import forms
from .models import TrenerProfile, HracProfile


# zakladni formular
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Uživatelské jméno',
            'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Heslo',
            'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )


# formular pro trenera
class TrenerProfileForm(forms.ModelForm):
    class Meta:
        model = TrenerProfile
        fields = ['first_name', 'last_name', 'phone', 'birth_date', 'club', 'photo']
        labels = {
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'phone': 'Telefonní číslo',
            'birth_date': 'Datum narození',
            'club': 'Klub',
            'photo': 'Fotografie',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Jméno',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Příjmení',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Telefonní číslo',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'club': forms.TextInput(attrs={
                'placeholder': 'Klub',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
        }


# formular pro hrace
class HracProfileForm(forms.ModelForm):
    class Meta:
        model = HracProfile
        trener = forms.ModelChoiceField(
            queryset=TrenerProfile.objects.all(),
            required=False,
            label="Vyberte trenéra"
        )
        fields = ['first_name', 'last_name', 'phone', 'birth_date', 'height', 'weight',
                  'cislo_dresu', 'pozice', 'preferred_foot', 'photo', 'trener']
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
            'trener': 'Trenér',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Jméno',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Příjmení',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Telefonní číslo',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'height': forms.NumberInput(attrs={
                'placeholder': 'Výška',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'weight': forms.NumberInput(attrs={
                'placeholder': 'Váha',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'cislo_dresu': forms.NumberInput(attrs={
                'placeholder': 'Číslo dresu',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'pozice': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'preferred_foot': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'trener': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
        }