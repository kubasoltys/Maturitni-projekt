from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import HracProfile, TrenerProfile

# Hlavní stránka
def index(request):
    return render(request, 'index.html')

# Přihlášení uživatele
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # prihlaseni na admina
            if user.is_superuser:
                return redirect('/admin/')
            # prihlaseni na hrace a trenera
            if hasattr(user, 'hracprofile'):
                return redirect('hrac_dashboard')
            elif hasattr(user, 'trenerprofile'):
                return redirect('trener_dashboard')
            else:
                return redirect('index')
        else:
            return render(request, 'login/login.html', {'error': 'Neplatné přihlašovací údaje'})
    return render(request, 'login/login.html')

# Dashboard hráče (zatím bez dat)
@login_required
def hrac_dashboard(request):
    hrac = request.user.hracprofile  # profil hráče
    return render(request, 'hrac/dashboard.html', {
        'hrac': hrac
    })


# Dashboard trenéra (zatím bez dat)
@login_required
def trener_dashboard(request):
    trener = request.user.trenerprofile  # profil trenéra
    return render(request, 'trener/dashboard.html', {
        'trener': trener
    })


# 1️⃣ Registrace – vytvoření uživatele
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')  # "hrac" nebo "trener"

        # kontrola duplicity
        if User.objects.filter(username=username).exists():
            return render(request, 'login/register.html', {'error': 'Uživatel již existuje.'})

        # vytvoření účtu
        user = User.objects.create_user(username=username, password=password)

        # vytvoření prázdného profilu podle role
        if role == 'hrac':
            HracProfile.objects.create(user=user)
            login(request, user)
            return redirect('register_hrac', user_id=user.id)
        elif role == 'trener':
            TrenerProfile.objects.create(user=user)
            login(request, user)
            return redirect('register_trener',user_id=user.id)

    return render(request, 'login/register.html')


# 2️⃣ Druhá část registrace – hráč
@login_required
def register_hrac(request, user_id):
    user = get_object_or_404(User, id=user_id)
    hrac_profile = request.user.hracprofile

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        trener_id = request.POST.get('trener')

        hrac_profile.first_name = first_name
        hrac_profile.last_name = last_name

        if trener_id:
            trener = TrenerProfile.objects.get(id=trener_id)
            hrac_profile.trener = trener

        hrac_profile.save()
        return redirect('hrac_dashboard')

    treneri = TrenerProfile.objects.all()
    return render(request, 'login/register_hrac.html', {'treneri': treneri})


# 2️⃣ Druhá část registrace – trenér
@login_required
def register_trener(request, user_id):
    user = get_object_or_404(User, id=user_id)
    trener_profile = request.user.trenerprofile

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        club = request.POST.get('club')

        trener_profile.first_name = first_name
        trener_profile.last_name = last_name
        trener_profile.club = club
        trener_profile.save()

        return redirect('trener_dashboard')

    return render(request, 'login/register_trener.html')


def logout_view(request):
    logout(request)
    return redirect('index')  # po odhlášení přesměruj na index

