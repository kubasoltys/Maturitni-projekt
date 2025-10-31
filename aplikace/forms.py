from django import forms
from .models import TrenerProfile, HracProfile


# prihlaseni
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Uživatelské jméno',
            'class': 'w-full p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Heslo',
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
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth_date', 'club', 'photo']
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

