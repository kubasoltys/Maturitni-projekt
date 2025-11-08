from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, TrenerProfileForm, HracProfileForm, TreninkForm
from .models import TrenerProfile, HracProfile, Trenink


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
            if user is not None and user.is_active:
                login(request, user)

                if user.is_superuser:
                    return redirect('/admin/')
                if hasattr(user, 'trenerprofile'):
                    profile = user.trenerprofile
                    dashboard_url = 'trener_dashboard'
                elif hasattr(user, 'hracprofile'):
                    profile = user.hracprofile
                    dashboard_url = 'hrac_dashboard'
                else:
                    profile = None
                    dashboard_url = 'index'

                if profile and not profile.first_name:
                    return redirect('first_login_view')

                return redirect(dashboard_url)

            else:
                # 🔥 TADY MUSÍ BÝT messages.error — ne message.error nebo něco jiného
                messages.error(request, 'Neplatné uživatelské jméno nebo heslo.')
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})



# prvni prihlaseni a doplneni profilu
def first_login_view(request):
    user = request.user
    if hasattr(user, 'trenerprofile'):
        ProfileForm = TrenerProfileForm
        instance = user.trenerprofile
    elif hasattr(user, 'hracprofile'):
        ProfileForm = HracProfileForm
        instance = user.hracprofile
    else:
        return redirect('index')  # nebo 404

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('hrac_dashboard' if hasattr(user, 'hracprofile') else 'trener_dashboard')
    else:
        form = ProfileForm(instance=instance)

    return render(request, 'login/first_login.html', {'form': form})



# dashboard hrace
@login_required
def hrac_dashboard(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        return render(request, 'index', {'message': 'Profil hráče nebyl nalezen.'})

    trener = hrac.trener
    context = {
        'hrac': hrac,
        'trener': trener,
    }
    return render(request, 'hrac/dashboard.html', context)


# dahboard trenera
@login_required
def trener_dashboard(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    hraci = trener.hrac.all()
    treninky = trener.treninky.all()

    context = {
        'trener': trener,
        'hraci': hraci,
        'treninky': treninky,
    }
    return render(request, 'trener/dashboard.html', context)



# editace profilu trenera
@login_required
def edit_trener_profile(request):
    trener = request.user.trenerprofile
    if request.method == 'POST':
        form = TrenerProfileForm(request.POST, request.FILES, instance=trener)
        if form.is_valid():
            form.save()
            return redirect('trener_dashboard')
    else:
        form = TrenerProfileForm(instance=trener)

    return render(request, 'trener/edit.html', {'form': form, 'trener': trener})


# editace profilu hrace
@login_required
def edit_hrac_profile(request):
    hrac = request.user.hracprofile
    if request.method == 'POST':
        form = HracProfileForm(request.POST, request.FILES, instance=hrac)
        if form.is_valid():
            form.save()
            return redirect('hrac_dashboard')
    else:
        form = HracProfileForm(instance=hrac)

    return render(request, 'hrac/edit.html', {'form': form, 'hrac': hrac})


# nastaveni hrace
@login_required
def trener_settings_view(request):
    user = request.user
    if not hasattr(user, 'trenerprofile'):
        return redirect('index')
    return render(request, 'trener/settings.html', {'user': user})


@login_required
def hrac_settings_view(request):
    user = request.user
    if not hasattr(user, 'hracprofile'):
        return redirect('index')
    return render(request, 'hrac/settings.html', {'user': user})


# detail uctu trenera
@login_required
def trener_account_view(request):
    profile = get_object_or_404(TrenerProfile, user=request.user)
    return render(request, 'trener/account.html', {'profile': profile})


# detail uctu hrace
@login_required
def hrac_account_view(request):
    profile = get_object_or_404(HracProfile, user=request.user)
    return render(request, 'hrac/account.html', {'profile': profile})


# logout
def logout_view(request):
    logout(request)
    return redirect('index')


# pridani treninku
@login_required
def add_trenink_view(request):
    if not hasattr(request.user, 'trenerprofile'):
        return redirect('index')

    trener = request.user.trenerprofile

    if request.method == 'POST':
        form = TreninkForm(request.POST)
        if form.is_valid():
            trenink = form.save(commit=False)
            trenink.trener = trener
            trenink.save()
            messages.success(request, 'Trénink byl úspěšně přidán.')
            return redirect('trener_dashboard')
    else:
        form = TreninkForm()

    return render(request, 'trener/trenink/add.html', {'form': form})


# uprava treninku
@login_required
def edit_trenink_view(request, trenink_id):
    trenink = get_object_or_404(Trenink, id=trenink_id, trener=request.user.trenerprofile)

    if request.method == 'POST':
        form = TreninkForm(request.POST, instance=trenink)
        if form.is_valid():
            form.save()
            messages.success(request, "Trénink byl aktualizován.")
            return redirect('trener_dashboard')
    else:
        form = TreninkForm(instance=trenink)

    return render(request, 'trener/trenink/edit.html', {'form': form, 'edit': True})


# smazani treninku
@login_required
def delete_trenink_view(request, trenink_id):
    trenink = get_object_or_404(Trenink, id=trenink_id, trener=request.user.trenerprofile)

    if request.method == 'POST':
        trenink.delete()
        messages.success(request, "Trénink byl úspěšně smazán.")
        return redirect('trener_dashboard')

    return redirect('trener_dashboard')