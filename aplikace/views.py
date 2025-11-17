from types import SimpleNamespace
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Q
from .forms import LoginForm, TrenerProfileForm, HracProfileForm, TreninkForm, ZapasForm, DohranyZapasForm
from .models import TrenerProfile, HracProfile, Trenink, DochazkaTreninky, Zapas, DochazkaZapasy, Tym


#----------------------------------------------------------------------------------------------
# hlavni stranka
#----------------------------------------------------------------------------------------------
def index(request):
    return render(request, 'index.html')


#----------------------------------------------------------------------------------------------
# prihlaseni
#----------------------------------------------------------------------------------------------
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
                    dashboard_url = 'trener_dashboard'
                elif hasattr(user, 'hracprofile'):
                    dashboard_url = 'hrac_dashboard'
                else:
                    dashboard_url = 'index'

                if user.first_login:
                    return redirect('first_login_view')

                return redirect(dashboard_url)

            else:
                messages.error(request, 'Neplatné uživatelské jméno nebo heslo.')
    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})


#----------------------------------------------------------------------------------------------
# prvni prihlaseni a doplneni profilu
#----------------------------------------------------------------------------------------------
def first_login_view(request):
    user = request.user

    if hasattr(user, 'trenerprofile'):
        ProfileForm = TrenerProfileForm
        instance = user.trenerprofile
        dashboard_url = 'trener_dashboard'
    elif hasattr(user, 'hracprofile'):
        ProfileForm = HracProfileForm
        instance = user.hracprofile
        dashboard_url = 'hrac_dashboard'
    else:
        return redirect('index')

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            user.first_login = False
            user.save()
            return redirect(dashboard_url)
    else:
        form = ProfileForm(instance=instance)

    return render(request, 'login/first_login.html', {'form': form})



# dashboard hrace
@login_required
def hrac_dashboard(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        return render(request, 'index.html', {'message': 'Profil hráče nebyl nalezen.'})

    trener = hrac.trener
    now = timezone.now()

    trenink = (
        Trenink.objects.filter(
            trener=trener,
            stav='Naplánováno',
            datum__gte=now.date()
        )
        .order_by('datum', 'cas')
        .prefetch_related('dochazka')
        .first()
    )

    treninky_data = []
    if trenink:
        dochazka_obj = trenink.dochazka.filter(hrac=hrac).first()
        treninky_data.append({
            'trenink': trenink,
            'dochazka': dochazka_obj,
            'hlasoval': dochazka_obj.pritomen is not None if dochazka_obj else False
        })

    zapas = (
        Zapas.objects.filter(
            trener=trener,
            datum__gt=now.date()
        )
        .order_by('datum', 'cas')
        .prefetch_related('dochazka')
        .first()
    )

    zapasy_data = []
    if zapas:
        dochazka_obj = zapas.dochazka.filter(hrac=hrac).first()
        zapasy_data.append({
            'zapas': zapas,
            'dochazka': dochazka_obj,
            'klub': hrac.trener.club,
            'hlasoval': dochazka_obj.pritomen is not None if dochazka_obj else False
        })

    context = {
        'hrac': hrac,
        'trener': trener,
        'treninky_data': treninky_data,
        'zapasy_data': zapasy_data,
    }

    return render(request, 'hrac/dashboard.html', context)


#---------------------------------------------------------------------------------
# dashboard trenera
#---------------------------------------------------------------------------------
@login_required
def trener_dashboard(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    tymy = Tym.objects.filter(trener=trener)
    hraci = HracProfile.objects.filter(tym__in=tymy).distinct()
    treninky = Trenink.objects.filter(tym__in=tymy, datum__gte=date.today()) \
                               .prefetch_related('dochazka', 'dochazka__hrac') \
                               .order_by('datum', 'cas')[:1]

    treninky_data = []
    for trenink in treninky:
        dochazka_dict = {d.hrac.id: d for d in trenink.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            dochazka_list.append(
                dochazka_dict.get(hrac.id, SimpleNamespace(hrac=hrac, pritomen=None, duvod=None))
            )
        treninky_data.append({
            'trenink': trenink,
            'dochazka_list': dochazka_list,
            'po_dohrani': trenink.stav != 'Naplánováno'
        })

    zapasy_qs = Zapas.objects.filter(tym__in=tymy, datum__gte=date.today()) \
                              .prefetch_related('dochazka', 'dochazka__hrac') \
                              .order_by('datum', 'cas')[:1]

    zapasy_data = []
    for zapas in zapasy_qs:
        dochazka_dict = {d.hrac.id: d for d in zapas.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            dochazka_list.append(
                dochazka_dict.get(hrac.id, SimpleNamespace(hrac=hrac, pritomen=None, duvod=None))
            )
        zapasy_data.append({
            'zapas': zapas,
            'dochazka_list': dochazka_list,
            'po_dohrani': zapas.stav != 'Naplánováno'
        })

    context = {
        'trener': trener,
        'hraci': hraci,
        'treninky_data': treninky_data,
        'zapasy': zapasy_data,
        'tymy': tymy,
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


#----------------------------------------------------------------------------------------------
# nastaveni trenera
#----------------------------------------------------------------------------------------------
@login_required
def trener_settings_view(request):
    user = request.user
    if not hasattr(user, 'trenerprofile'):
        return redirect('index')

    trener = user.trenerprofile
    tymy = Tym.objects.filter(trener=trener)

    return render(request, 'trener/settings.html', {
        'trener': trener,
        'tymy': tymy,
    })



# nastaveni hrace
@login_required
def hrac_settings_view(request):
    user = request.user
    if not hasattr(user, 'hracprofile'):
        return redirect('index')

    hrac = user.hracprofile
    trener = hrac.trener

    context = {
        'user': user,
        'hrac': hrac,
        'trener': trener,
    }

    return render(request, 'hrac/settings.html', context)


#----------------------------------------------------------------------------------------------
# detail uctu trenera
#----------------------------------------------------------------------------------------------
@login_required
def trener_account_view(request):
    trener = get_object_or_404(TrenerProfile, user=request.user)
    tymy = Tym.objects.filter(trener=trener)

    return render(request, 'trener/account.html', {
        'trener': trener,
        'tymy': tymy,
    })



# detail účtu hráče
@login_required
def hrac_account_view(request):
    hrac = get_object_or_404(HracProfile, user=request.user)
    trener = hrac.trener  # informace o trenérovi, pokud existuje

    context = {
        'hrac': hrac,
        'trener': trener,
    }

    return render(request, 'hrac/account.html', context)



# logout
def logout_view(request):
    logout(request)
    return redirect('index')



# TRENINKY


#--------------------------------------------------------------------------------
# trener - stranka pro treninky
#--------------------------------------------------------------------------------
@login_required
def trener_trenink(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    tymy = Tym.objects.filter(trener=trener)
    hraci = HracProfile.objects.filter(tym__in=tymy).distinct()
    treninky = Trenink.objects.filter(tym__in=tymy, datum__gte=date.today()) \
                               .prefetch_related('dochazka', 'dochazka__hrac') \
                               .order_by('datum', 'cas')

    treninky_data = []
    for trenink in treninky:
        dochazka_dict = {d.hrac.id: d for d in trenink.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            dochazka_list.append(
                dochazka_dict.get(hrac.id, SimpleNamespace(hrac=hrac, pritomen=None, duvod=None))
            )
        treninky_data.append({
            'trenink': trenink,
            'dochazka_list': dochazka_list,
            'po_dohrani': trenink.stav != 'Naplánováno'
        })

    context = {
        'trener': trener,
        'hraci': hraci,
        'treninky_data': treninky_data,
        'tymy': tymy,
    }
    return render(request, 'trener/trenink/trenink.html', context)


#------------------------------------------------------------------------------------------------------------
# trener -historie treninku
#------------------------------------------------------------------------------------------------------------
@login_required
def trener_trenink_historie(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    tymy = Tym.objects.filter(trener=trener)
    hraci = HracProfile.objects.filter(tym__in=tymy).distinct()

    treninky = (
        Trenink.objects.filter(tym__in=tymy, datum__lt=date.today())
        .prefetch_related('dochazka', 'dochazka__hrac')
        .order_by('-datum', '-cas')
    )

    treninky_data = []
    for trenink in treninky:
        dochazka_dict = {d.hrac.id: d for d in trenink.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            dochazka_list.append(
                dochazka_dict.get(hrac.id, SimpleNamespace(hrac=hrac, pritomen=None, duvod=None))
            )
        treninky_data.append({'trenink': trenink, 'dochazka_list': dochazka_list})

    context = {
        'trener': trener,
        'hraci': hraci,
        'treninky_data': treninky_data,
        'tymy': tymy,
    }
    return render(request, 'trener/trenink/trenink_historie.html', context)


#------------------------------------------------------------------------------------------------------------------
# pridani treninku
#------------------------------------------------------------------------------------------------------------------
@login_required
def add_trenink_view(request):
    if not hasattr(request.user, 'trenerprofile'):
        return redirect('index')

    trener = request.user.trenerprofile
    tymy = Tym.objects.filter(trener=trener)
    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        form = TreninkForm(request.POST, trener=trener)
        if form.is_valid():
            trenink = form.save()
            messages.success(request, 'Trénink byl úspěšně přidán.')
            return redirect(zpet)
    else:
        form = TreninkForm(trener=trener)

    return render(request, 'trener/trenink/add.html', {'form': form, 'tymy': tymy})


#----------------------------------------------------------------------------------------------------------------
# uprava treninku
#----------------------------------------------------------------------------------------------------------------
@login_required
def edit_trenink_view(request, trenink_id):
    trener = request.user.trenerprofile
    trenink = get_object_or_404(Trenink, id=trenink_id, tym__trener=trener)
    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        form = TreninkForm(request.POST, instance=trenink, trener=trener)
        if form.is_valid():
            form.save()
            messages.success(request, "Trénink byl aktualizován.")
            return redirect(zpet)
    else:
        form = TreninkForm(instance=trenink, trener=trener)

    return render(request, 'trener/trenink/edit.html', {'form': form, 'edit': True})


#------------------------------------------------------------------------------------------------------------------
# smazani treninku
#------------------------------------------------------------------------------------------------------------------
@login_required
def delete_trenink_view(request, trenink_id):
    trener = request.user.trenerprofile
    trenink = get_object_or_404(Trenink, id=trenink_id, tym__trener=trener)
    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        trenink.delete()
        messages.success(request, "Trénink byl úspěšně smazán.")
        return redirect(zpet)

    return redirect(zpet)



# hlasovani pro hrace o treninku
@login_required
def hlasovani_dochazka_view(request, trenink_id):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte hráčský profil.")
        return redirect('index')

    trenink = get_object_or_404(Trenink, id=trenink_id, trener=hrac.trener)
    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        pritomen_raw = request.POST.get('pritomen')
        if pritomen_raw not in ('true', 'false'):
            messages.error(request, "Neplatná volba.")
            return redirect('hrac_dashboard')

        pritomen = (pritomen_raw == 'true')
        duvod = request.POST.get('duvod', '').strip() or None

        dochazka_obj, created = DochazkaTreninky.objects.update_or_create(
            trenink=trenink,
            hrac=hrac,
            defaults={'pritomen': pritomen, 'duvod': duvod}
        )

        messages.success(request, "Tvá docházka byla uložena.")
        return redirect(zpet)

    return redirect(zpet)



# zrusit hlasovani na trenink
@login_required
def hlasovani_dochazka_smazat(request, trenink_id):
    hrac = request.user.hracprofile
    trenink = get_object_or_404(Trenink, id=trenink_id)
    zpet = request.META.get('HTTP_REFERER', '/')

    dochazka_obj = DochazkaTreninky.objects.filter(trenink=trenink, hrac=hrac).first()
    if dochazka_obj:
        dochazka_obj.pritomen = None
        dochazka_obj.duvod = ''
        dochazka_obj.save()
        messages.success(request, "Volba byla odstraněna.")
    return redirect(zpet)



# hrac - stranka pro treninky
@login_required
def hrac_trenink(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        return render(request, 'index.html', {'message': 'Profil hráče nebyl nalezen.'})

    dnes = date.today()

    treninky = Trenink.objects.filter(
        trener=hrac.trener,
        stav='Naplánováno',
        datum__gte=dnes
    ).order_by('datum', 'cas')

    treninky_data = []
    for trenink in treninky:
        dochazka_obj = trenink.dochazka.filter(hrac=hrac).first()
        treninky_data.append({
            'trenink': trenink,
            'dochazka': dochazka_obj,
            'hlasoval': dochazka_obj.pritomen is not None if dochazka_obj else False
        })

    return render(request, 'hrac/trenink/trenink.html', {
        'hrac': hrac,
        'trener': hrac.trener,
        'treninky_data': treninky_data,
    })



# hrac - historie treninku
@login_required
def hrac_trenink_historie(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        return render(request, 'index.html', {'message': 'Profil hráče nebyl nalezen.'})

    dnes = date.today()

    treninky = Trenink.objects.filter(
        trener=hrac.trener,
        datum__lt=dnes
    ).order_by('datum', 'cas')

    treninky_data = []
    for trenink in treninky:
        dochazka_obj = trenink.dochazka.filter(hrac=hrac).first()
        treninky_data.append({
            'trenink': trenink,
            'dochazka': dochazka_obj,
            'hlasoval': dochazka_obj.pritomen is not None if dochazka_obj else False
        })

    return render(request, 'hrac/trenink/trenink_historie.html', {
        'hrac': hrac,
        'trener': hrac.trener,
        'treninky_data': treninky_data,
    })



# ZAPASY



# hrac - stranka pro zapasy
@login_required
def hrac_zapas(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte profil.")
        return redirect('index')

    now = timezone.localtime(timezone.now())

    zapasy = (
        Zapas.objects.filter(trener=hrac.trener, stav='Naplánováno')
        .filter(datum__gte=now.date())
        .order_by('datum', 'cas')
    )

    zapasy_data = []
    for zapas in zapasy:
        datetime_zapasu = timezone.make_aware(
            timezone.datetime.combine(zapas.datum, zapas.cas)
        )
        if datetime_zapasu <= now:
            continue

        dochazka_obj = zapas.dochazka.filter(hrac=hrac).first()
        zapasy_data.append({
            'zapas': zapas,
            'dochazka': dochazka_obj,
            'klub': hrac.trener.club,
            'hlasoval': dochazka_obj.pritomen is not None if dochazka_obj else False,
            'po_dohrani': (
                datetime_zapasu < now
                and (zapas.vysledek_domaci is None or zapas.vysledek_hoste is None)
            )
        })

    return render(request, 'hrac/zapas/zapas.html', {
        'hrac': hrac,
        'trener': hrac.trener,
        'zapasy_data': zapasy_data
    })



# hlasovani pro hrace o zapasu
@login_required
def hrac_hlasovani_zapas(request, zapas_id):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte hráčský profil.")
        return redirect('index')

    zapas = get_object_or_404(Zapas, id=zapas_id, trener=hrac.trener)
    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        pritomen_raw = request.POST.get('pritomen')
        if pritomen_raw not in ('true', 'false'):
            messages.error(request, "Neplatná volba.")
            return redirect('hrac_zapasy')

        pritomen = pritomen_raw == 'true'

        DochazkaZapasy.objects.update_or_create(
            zapas=zapas,
            hrac=hrac,
            defaults={'pritomen': pritomen}
        )

        messages.success(request, "Tvá účast byla zaznamenána.")
        return redirect(zpet)

    return redirect(zpet)



# zrusit hlasovani na zapas
@login_required
def hrac_hlasovani_zapas_smazat(request, zapas_id):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte hráčský profil.")
        return redirect('index')

    zapas = get_object_or_404(Zapas, id=zapas_id)
    dochazka = zapas.dochazka.filter(hrac=hrac).first()
    zpet = request.META.get('HTTP_REFERER', '/')
    if dochazka:
        dochazka.pritomen = None
        dochazka.save()
        messages.success(request, "Volba byla zrušena.")
    return redirect(zpet)



# trener - stranka pro zapasy
@login_required
def trener_zapas(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    hraci = list(trener.hrac.all())

    zapasy = (
        trener.zapasy
        .filter(stav='Naplánováno')
        .prefetch_related('dochazka', 'dochazka__hrac')
        .order_by('datum', 'cas')
    )

    zapasy_data = []
    now = timezone.now()

    for zapas in zapasy:
        dochazka_dict = {d.hrac.id: d for d in zapas.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            if hrac.id in dochazka_dict:
                dochazka_list.append(dochazka_dict[hrac.id])
            else:
                from types import SimpleNamespace
                dochazka_list.append(SimpleNamespace(
                    hrac=hrac,
                    pritomen=None,
                    poznamka=None
                ))

        zapas_datetime_naive = datetime.combine(zapas.datum, zapas.cas)
        zapas_datetime = timezone.make_aware(zapas_datetime_naive, timezone.get_current_timezone())

        po_dohrani = (zapas_datetime < now and
                        (zapas.vysledek_tymu is None or zapas.vysledek_soupere is None))

        zapasy_data.append({
            'zapas': zapas,
            'dochazka_list': dochazka_list,
            'po_dohrani': po_dohrani
        })

    context = {
        'trener': trener,
        'hraci': hraci,
        'zapasy_data': zapasy_data,
    }

    return render(request, 'trener/zapas/zapas.html', context)



# pridani zapasu
@login_required
def add_zapas_view(request):
    if not hasattr(request.user, 'trenerprofile'):
        return redirect('index')

    trener = request.user.trenerprofile

    if request.method == 'POST':
        form = ZapasForm(request.POST)
        if form.is_valid():
            zapas = form.save(commit=False)
            zapas.trener = trener
            zapas.save()
            messages.success(request, 'Zápas byl úspěšně přidán.')
            return redirect('trener_zapas')
    else:
        form = ZapasForm()

    return render(request, 'trener/zapas/add.html', {'form': form})



# uprave zapasu
@login_required
def edit_zapas_view(request, zapas_id):
    zapas = get_object_or_404(Zapas, id=zapas_id, trener=request.user.trenerprofile)

    if request.method == 'POST':
        form = ZapasForm(request.POST, instance=zapas)
        if form.is_valid():
            form.save()
            messages.success(request, "Zápas byl aktualizován.")
            return redirect('trener_zapas')
    else:
        form = ZapasForm(instance=zapas)

    return render(request, 'trener/zapas/edit.html', {'form': form, 'edit': True})



# smazani zapasu
@login_required
def delete_zapas_view(request, zapas_id):
    zapas = get_object_or_404(Zapas, id=zapas_id, trener=request.user.trenerprofile)
    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        zapas.delete()
        messages.success(request, "Zápas byl úspěšně smazán.")
        return redirect(zpet)

    return redirect(zpet)



# oznaceni zapasu jako odehrany
@login_required
def oznacit_dohrano_view(request, zapas_id):
    zapas = get_object_or_404(Zapas, id=zapas_id, trener=request.user.trenerprofile)

    if request.method == 'POST':
        form = DohranyZapasForm(request.POST, instance=zapas)
        if form.is_valid():
            zapas = form.save(commit=False)
            zapas.stav = 'Dohráno'
            zapas.save()
            return redirect('trener_zapas')  # nebo speciální stránka pro dohrané zápasy
    else:
        form = DohranyZapasForm(instance=zapas)

    return render(request, 'trener/zapas/oznacit_dohrano.html', {'form': form, 'zapas': zapas})



# trener - odehrany zapasy
@login_required
def trener_dohrane_zapasy(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    hraci = list(trener.hrac.all())

    zapasy = (
        trener.zapasy
        .filter(stav='Dohráno')
        .prefetch_related('dochazka', 'dochazka__hrac')
        .order_by('datum', 'cas')
    )

    zapasy_data = []
    for zapas in zapasy:
        dochazka_dict = {d.hrac.id: d for d in zapas.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            if hrac.id in dochazka_dict:
                dochazka_list.append(dochazka_dict[hrac.id])
            else:
                from types import SimpleNamespace
                dochazka_list.append(SimpleNamespace(
                    hrac=hrac,
                    pritomen=None,
                    poznamka=None
                ))
        zapasy_data.append({'zapas': zapas, 'dochazka_list': dochazka_list})

    context = {
        'trener': trener,
        'hraci': hraci,
        'zapasy_data': zapasy_data,
    }

    return render(request, 'trener/zapas/zapas_dohrano.html', context)



# hrac - dohrane zapasy
@login_required
def hrac_dohrane_zapasy(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte hráčský profil.")
        return redirect('index')

    dnes = timezone.localdate()
    tren = hrac.trener

    zapasy = Zapas.objects.filter(
        trener=tren
    ).filter(
        Q(stav='Dohráno') |
        Q(stav='Naplánováno', datum__lt=dnes)
    ).order_by('datum', 'cas')

    zapasy_data = []

    for zapas in zapasy:
        dochazka_obj = zapas.dochazka.filter(hrac=hrac).first()
        zapasy_data.append({
            'zapas': zapas,
            'dochazka': dochazka_obj,
            'vysledek_tymu': getattr(zapas, 'vysledek_tymu', None),
            'vysledek_soupere': getattr(zapas, 'vysledek_soupere', None)
        })

    context = {
        'hrac': hrac,
        'trener': tren,
        'zapasy_data': zapasy_data
    }

    return render(request, 'hrac/zapas/zapas_dohrano.html', context)