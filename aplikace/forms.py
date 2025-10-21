from django import forms
from django.contrib.auth.models import User
from .models import HracProfile, TrenerProfile


# login formular
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


# registrace formular
class RegisterForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('hrac', 'Hráč'),
        ('trener', 'Trenér'),
    ]
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400',
            'placeholder': 'Heslo'
        })
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400',
            'placeholder': 'Znovu heslo'
        })
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="",
        widget=forms.Select(attrs={
            'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
        })
    )
    class Meta:
        model = User
        fields = ['username']
        labels = {'username': ''}
        help_texts = {'username': ''}
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400',
                'placeholder': 'Uživatelské jméno'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Hesla se neshodují.")

        return cleaned_data


# registrace hrace formular
class RegisterFormHrac(forms.ModelForm):
    class Meta:
        model = HracProfile
        fields = ['first_name', 'last_name', 'vek', 'pozice', 'cislo_dresu', 'trener']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Jméno',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Příjmení',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'vek': forms.NumberInput(attrs={
                'placeholder': 'Věk',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400',
                'min': 10,
                'max': 100,
            }),
            'pozice': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'cislo_dresu': forms.NumberInput(attrs={
                'placeholder': 'Číslo dresu',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'trener': forms.Select(attrs={
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
        }


#registrace trenera formular
class RegisterFormTrener(forms.ModelForm):
    class Meta:
        model = TrenerProfile
        fields = ['first_name', 'last_name', 'club']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Jméno',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Příjmení',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
            'club': forms.TextInput(attrs={
                'placeholder': 'Název klubu',
                'class': 'w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'
            }),
        }
