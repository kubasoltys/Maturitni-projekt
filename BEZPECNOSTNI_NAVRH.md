# Bezpečnostní návrh pro vytváření účtů hráčů

## Problémy s navrženým postupem:

1. **Provizorní heslo v e-mailu** - Pokud se e-mail dostane do špatných rukou, útočník může získat přístup
2. **Čekání na stránce** - Neideální UX, uživatel může zavřít stránku
3. **Dvojí přihlášení** - Zbytečně složitý proces
4. **Chybí expirace** - Tokeny by měly expirovat po určité době

## Doporučené bezpečnější řešení:

### Varianta 1: Token-based aktivace (DOPORUČENO)

**Workflow:**
1. Admin vytvoří účet s e-mailem (bez hesla nebo s dočasným heslem)
2. Systém vygeneruje bezpečný, jednorázový token s expirací (např. 7 dní)
3. Pošle se e-mail s odkazem obsahujícím token
4. Hráč klikne na odkaz → ověří se token → nastaví si heslo a dokončí registraci

**Výhody:**
- ✅ Bezpečný token (cryptographically secure)
- ✅ Jednorázový (pouze jedno použití)
- ✅ Expirace (automatické vypršení)
- ✅ Jednoduchý UX (jeden klik)
- ✅ Žádné provizorní heslo v e-mailu

### Varianta 2: Dvoufázová aktivace (kompromis)

**Workflow:**
1. Admin vytvoří účet s e-mailem
2. Pošle se e-mail s oznámením a tokenem
3. Hráč zadá e-mail na stránce → systém pošle další e-mail s aktivačním odkazem
4. Hráč klikne na odkaz → nastaví si heslo a dokončí registraci

**Výhody:**
- ✅ Bezpečnější než původní návrh
- ✅ Uživatel aktivně žádá o aktivaci

**Nevýhody:**
- ⚠️ Dva e-maily místo jednoho
- ⚠️ Složitější workflow

## Implementace - Varianta 1 (DOPORUČENO)

### 1. Rozšíření User modelu

```python
# models.py
from django.utils import timezone
from datetime import timedelta
import secrets

class User(AbstractUser):
    # ... existující pole ...
    
    activation_token = models.CharField(max_length=64, blank=True, null=True)
    activation_token_expires = models.DateTimeField(blank=True, null=True)
    is_activated = models.BooleanField(default=False)
    
    def generate_activation_token(self):
        """Vygeneruje bezpečný token s expirací 7 dní"""
        self.activation_token = secrets.token_urlsafe(32)
        self.activation_token_expires = timezone.now() + timedelta(days=7)
        self.save()
        return self.activation_token
    
    def is_activation_token_valid(self):
        """Zkontroluje, zda je token platný a neexpiroval"""
        if not self.activation_token or not self.activation_token_expires:
            return False
        return timezone.now() < self.activation_token_expires
```

### 2. View pro vytvoření účtu adminem

```python
# views.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

@login_required
def admin_create_player(request):
    if not request.user.is_superuser:
        return redirect('index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        # Vytvoření uživatele s dočasným heslem
        temp_password = User.objects.make_random_password()
        user = User.objects.create_user(
            username=email,  # nebo jiný unikátní username
            email=email,
            password=temp_password,
            role='hrac',
            is_active=False,  # Neaktivní dokud neaktivuje
            first_login=True
        )
        
        # Vytvoření profilu
        HracProfile.objects.create(user=user)
        
        # Vygenerování tokenu
        token = user.generate_activation_token()
        
        # Odeslání e-mailu
        activation_url = request.build_absolute_uri(
            f'/activate/{user.id}/{token}/'
        )
        
        send_mail(
            subject='Váš účet byl vytvořen - Squadra',
            message=f'Váš účet byl vytvořen. Pro aktivaci klikněte na: {activation_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=render_to_string('emails/account_created.html', {
                'user': user,
                'activation_url': activation_url
            })
        )
        
        messages.success(request, f'Účet pro {email} byl vytvořen a e-mail byl odeslán.')
        return redirect('admin_create_player')
    
    return render(request, 'admin/create_player.html')
```

### 3. View pro aktivaci účtu

```python
# views.py
def activate_account(request, user_id, token):
    try:
        user = User.objects.get(pk=user_id)
        
        # Ověření tokenu
        if not user.activation_token or user.activation_token != token:
            messages.error(request, 'Neplatný aktivační odkaz.')
            return redirect('login')
        
        if not user.is_activation_token_valid():
            messages.error(request, 'Aktivační odkaz vypršel. Kontaktujte administrátora.')
            return redirect('login')
        
        if user.is_activated:
            messages.info(request, 'Účet je již aktivován.')
            return redirect('login')
        
        # Aktivace účtu
        user.is_active = True
        user.is_activated = True
        user.activation_token = None  # Token použít pouze jednou
        user.activation_token_expires = None
        user.save()
        
        # Přihlášení uživatele
        login(request, user)
        
        messages.success(request, 'Váš účet byl úspěšně aktivován!')
        return redirect('first_login_view')
        
    except User.DoesNotExist:
        messages.error(request, 'Uživatel nebyl nalezen.')
        return redirect('login')
```

### 4. Nastavení e-mailu v settings.py

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # nebo jiný SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@squadra.cz'
```

### 5. URL konfigurace

```python
# urls.py
urlpatterns = [
    # ...
    path('activate/<int:user_id>/<str:token>/', views.activate_account, name='activate_account'),
]
```

## Bezpečnostní opatření:

1. ✅ **Bezpečný token** - `secrets.token_urlsafe()` místo náhodného řetězce
2. ✅ **Exspirace** - Token expiruje po 7 dnech
3. ✅ **Jednorázové použití** - Token se smaže po použití
4. ✅ **HTTPS** - V produkci vždy používat HTTPS
5. ✅ **Rate limiting** - Omezit počet pokusů o aktivaci
6. ✅ **Logování** - Logovat všechny aktivační pokusy

## Alternativní řešení s Django allauth:

Pokud chcete použít hotové řešení, můžete použít `django-allauth`, který má:
- E-mailové ověření
- Bezpečné tokeny
- Expirace
- Rate limiting
- A další bezpečnostní funkce

## Závěr:

**Doporučuji Variantu 1** - je nejbezpečnější, nejjednodušší pro uživatele a standardní v moderních aplikacích.

