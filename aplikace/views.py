from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import HracProfile, TrenerProfile
from .forms import LoginForm, RegisterForm, RegisterFormHrac, RegisterFormTrener


# hlavni stranka
def index(request):
    return render(request, 'index.html')


# prihlaseni
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Přesměrování podle role
                if user.is_superuser:
                    return redirect('/admin/')
                elif hasattr(user, 'hracprofile'):
                    return redirect('hrac_dashboard')
                elif hasattr(user, 'trenerprofile'):
                    return redirect('trener_dashboard')
                else:
                    return redirect('index')
            else:
                form.add_error(None, "Neplatné přihlašovací údaje")
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})



# 1. registrace
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            password = form.cleaned_data.get('password1')
            user = form.save(commit=False)
            user.set_password(password)
            user.save()
            login(request, user)
            if role == 'hrac':
                HracProfile.objects.get_or_create(user=user)
                return redirect('register_hrac', user_id=user.id)
            elif role == 'trener':
                TrenerProfile.objects.get_or_create(user=user)
                return redirect('register_trener', user_id=user.id)

            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'login/register.html', {'form': form})


# 2. registrace hrace
@login_required
def register_hrac(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user != user and not request.user.is_superuser:
        return redirect('index')

    hrac_profile, created = HracProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = RegisterFormHrac(request.POST, instance=hrac_profile)
        if form.is_valid():
            form.save()
            return redirect('hrac_dashboard')
    else:
        form = RegisterFormHrac(instance=hrac_profile)

    treneri = TrenerProfile.objects.all()
    return render(request, 'login/register_hrac.html', {'form': form, 'treneri': treneri})


# 2. registrace trenera
@login_required
def register_trener(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user != user and not request.user.is_superuser:
        return redirect('index')

    trener_profile, created = TrenerProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = RegisterFormTrener(request.POST, instance=trener_profile)
        if form.is_valid():
            form.save()
            return redirect('trener_dashboard')
    else:
        form = RegisterFormTrener(instance=trener_profile)

    return render(request, 'login/register_trener.html', {'form': form})


# dashboard hrace
@login_required
def hrac_dashboard(request):
    hrac = request.user.hracprofile
    return render(request, 'hrac/dashboard.html', {'hrac': hrac})


# dashboard trenera
@login_required
def trener_dashboard(request):
    trener = request.user.trenerprofile
    hraci = HracProfile.objects.filter(trener=trener)
    return render(request, 'trener/dashboard.html', {'trener': trener, 'hraci': hraci})


# logout
def logout_view(request):
    logout(request)
    return redirect('index')