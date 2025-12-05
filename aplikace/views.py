from types import SimpleNamespace
from django.contrib.auth.decorators import login_required
from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.utils.timezone import now

from .forms import LoginForm, TrenerProfileForm, HracProfileForm, TreninkForm, ZapasForm, DohranyZapasForm
from .models import TrenerProfile, HracProfile, Trenink, DochazkaTreninky, Zapas, DochazkaZapasy, Tym, Gol, Karta
import json


#----------------------------------------------------------------------------------------------
# hlavni stranka
#----------------------------------------------------------------------------------------------
def index(request):
    return render(request, 'index.html')



# LOGIN


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


#----------------------------------------------------------------------------------------------
# logout
#----------------------------------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return redirect('index')



# DASHBOARDY


#-----------------------------------------------------------------------------------------------
# dashboard hrace
#-----------------------------------------------------------------------------------------------
@login_required
def hrac_dashboard(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        return render(request, 'index.html', {'message': 'Profil hráče nebyl nalezen.'})

    tym = hrac.tym
    trener = tym.trener
    now = timezone.now()

    treninky_qs = Trenink.objects.filter(
        tym=tym,
        stav='Naplánováno'
    ).order_by('datum', 'cas').prefetch_related('dochazka')

    treninky_data = []
    for trenink in treninky_qs:
        trenink_datetime = timezone.make_aware(
            datetime.combine(trenink.datum, trenink.cas),
            timezone.get_current_timezone()
        )
        if trenink_datetime < now:
            continue

        dochazka_obj = trenink.dochazka.filter(hrac=hrac).first()
        treninky_data.append({
            'trenink': trenink,
            'dochazka': dochazka_obj,
            'hlasoval': dochazka_obj.pritomen is not None if dochazka_obj else False
        })

    zapasy_qs = Zapas.objects.filter(
        tym=tym,
        stav='Naplánováno'
    ).order_by('datum', 'cas').prefetch_related('dochazka')

    zapasy_data = []
    for zapas in zapasy_qs:
        zapas_datetime = timezone.make_aware(
            datetime.combine(zapas.datum, zapas.cas),
            timezone.get_current_timezone()
        )
        if zapas_datetime < now:
            continue

        dochazka_obj = zapas.dochazka.filter(hrac=hrac).first()
        zapasy_data.append({
            'zapas': zapas,
            'dochazka': dochazka_obj,
            'klub': tym.nazev,
            'hlasoval': dochazka_obj.pritomen is not None if dochazka_obj else False
        })

    context = {
        'hrac': hrac,
        'trener': trener,
        'tym': tym,
        'treninky_data': treninky_data,
        'zapasy_data': zapasy_data,
    }

    return render(request, 'hrac/dashboard.html', context)


#--------------------------------------------------------------------------------------------------
# dashboard trenera
#--------------------------------------------------------------------------------------------------
@login_required
def trener_dashboard(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    tymy = Tym.objects.filter(trener=trener)

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    hraci = HracProfile.objects.filter(tym=vybrany_tym).distinct()
    now = timezone.now()

    treninky_qs = Trenink.objects.filter(
        tym=vybrany_tym,
        stav='Naplánováno'
    ).order_by('datum', 'cas').prefetch_related('dochazka', 'dochazka__hrac')

    treninky_data = []
    for trenink in treninky_qs:
        trenink_datetime = timezone.make_aware(
            datetime.combine(trenink.datum, trenink.cas),
            timezone.get_current_timezone()
        )
        if trenink_datetime < now:
            continue

        dochazka_dict = {d.hrac.id: d for d in trenink.dochazka.all()}

        dochazka_list = []
        for hrac in hraci:
            dochazka_list.append(
                dochazka_dict.get(
                    hrac.id,
                    SimpleNamespace(hrac=hrac, pritomen=None, duvod=None)
                )
            )

        treninky_data.append({
            'trenink': trenink,
            'dochazka_list': dochazka_list,
            'po_dohrani': trenink_datetime < now or trenink.stav != 'Naplánováno'
        })

    zapasy_qs = (
        Zapas.objects.filter(tym=vybrany_tym, stav='Naplánováno')
                     .prefetch_related('dochazka', 'dochazka__hrac')
                     .order_by('datum', 'cas')
    )

    nejblizsi = None

    for zapas in zapasy_qs:
        zapas_datetime = timezone.make_aware(
            datetime.combine(zapas.datum, zapas.cas),
            timezone.get_current_timezone()
        )

        po_casove = zapas_datetime < now

        if not po_casove:
            nejblizsi = zapas
            break

        if po_casove:
            nejblizsi = zapas
            break

    zapasy_data = []

    if nejblizsi:
        dochazka_dict = {d.hrac.id: d for d in nejblizsi.dochazka.all()}

        dochazka_list = [
            dochazka_dict.get(
                hrac.id,
                SimpleNamespace(hrac=hrac, pritomen=None, duvod=None)
            )
            for hrac in hraci
        ]

        zapas_datetime = timezone.make_aware(
            datetime.combine(nejblizsi.datum, nejblizsi.cas),
            timezone.get_current_timezone()
        )

        po_dohrani = zapas_datetime < now

        zapasy_data.append({
            'zapas': nejblizsi,
            'dochazka_list': dochazka_list,
            'po_dohrani': po_dohrani,
        })

    context = {
        'trener': trener,
        'vybrany_tym': vybrany_tym,
        'hraci': hraci,
        'treninky_data': treninky_data,
        'zapasy': zapasy_data,
        'tymy': tymy,
    }

    return render(request, 'trener/dashboard.html', context)



#---------------------------------------------------------------------------------------------
# trener - stranka pro zobrazeni hracu
#---------------------------------------------------------------------------------------------
@login_required
def trener_hraci_view(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, "error.html", {"message": "Nemáte trenérský profil."})

    tymy = Tym.objects.filter(trener=trener)

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    hraci = HracProfile.objects.filter(tym=vybrany_tym).select_related("user", "tym")
    hraci = list(hraci)
    hraci.sort(key=lambda x: x.dochazka_treninky, reverse=True)

    return render(request, "trener/hraci/hraci.html", {
        'hraci': hraci,
        'tymy': tymy,
        'vybrany_tym': vybrany_tym,
        'trener': trener,
    })


#----------------------------------------------------------------------------------------------
# trener - statistiky hrace
#----------------------------------------------------------------------------------------------
@login_required
def trener_hrac_statistiky(request, hrac_id):

    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, "error.html", {"message": "Nemáte trenérský profil."})

    tymy = Tym.objects.filter(trener=trener)

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    hrac = get_object_or_404(HracProfile, id=hrac_id)

    if hrac.tym not in trener.tymy.all():
        return render(request, "error.html", {"message": "Nemáte oprávnění zobrazit tohoto hráče."})

    goly = Gol.objects.filter(hrac=hrac)
    karty = Karta.objects.filter(hrac=hrac)

    gol_count = goly.count()
    asistence_count = Gol.objects.filter(asistence=hrac).count()
    zlute = karty.filter(typ="zluta").count()
    cervene = karty.filter(typ__in=["cervena", "zluta_cervena"]).count()

    dochazka_treninky = (
        DochazkaTreninky.objects
        .filter(hrac=hrac)
        .select_related("trenink")
        .order_by("-trenink__datum")[:4]
    )

    dochazka_hrace_zapasy = (
        DochazkaZapasy.objects
        .filter(hrac=hrac, pritomen=True)
        .select_related("zapas")
        .order_by("zapas__datum")
    )

    zapasy = (
        Zapas.objects.filter(tym=vybrany_tym, stav="Dohráno")
        .prefetch_related("goly", "karty", "dochazka")
        .order_by("-datum", "-cas")
    )

    zapasy_data = []

    for zapas in zapasy:
        dochazka_hrace = dochazka_hrace_zapasy.filter(zapas=zapas).first()
        if dochazka_hrace:
            goly_hrace = zapas.goly.filter(hrac=hrac)
            karty_hrace = zapas.karty.filter(hrac=hrac)
            goly_tym = zapas.goly.filter(hrac__tym=vybrany_tym).count()
            vysledek_soupere = zapas.vysledek_soupere
            asistence_hrace = zapas.goly.filter(asistence=hrac)

            zapasy_data.append({
                "zapas": zapas,
                "goly_hrace": goly_hrace,
                "karty_hrace": karty_hrace,
                "vysledek_tymu": goly_tym,
                "vysledek_soupere": vysledek_soupere,
                "asistence_hrace": asistence_hrace,
            })

    labels = []
    values = []

    for d in dochazka_hrace_zapasy:
        zapas = d.zapas
        pocet = zapas.goly.filter(hrac=hrac).count()

        labels.append(zapas.datum.strftime("%d.%m.%Y"))
        values.append(pocet)

    graf_goly_json = json.dumps({
        "labels": labels,
        "values": values,
    })

    zapasy_pritomen_ids = dochazka_hrace_zapasy.values_list('zapas', flat=True)
    celkove_goly = Gol.objects.filter(hrac=hrac, zapas__in=zapasy_pritomen_ids).count()
    celkove_asistence = Gol.objects.filter(asistence=hrac,
                                           zapas__in=zapasy_pritomen_ids).count()
    pocet_zapasu = len(zapasy_pritomen_ids)
    prumer_golu = round(celkove_goly / pocet_zapasu, 2) if pocet_zapasu > 0 else 0
    prumer_asistenci = round(celkove_asistence / pocet_zapasu, 2) if pocet_zapasu > 0 else 0

    context = {
        "hrac": hrac,
        "tym": hrac.tym,
        "vybrany_tym": vybrany_tym,
        "trener": trener,
        "goly": goly,
        "karty": karty,
        "gol_count": gol_count,
        "asistence_count": asistence_count,
        "zlute": zlute,
        "cervene": cervene,
        "prumer_golu": prumer_golu,
        "prumer_asistenci": prumer_asistenci,
        "dochazka_treninky": dochazka_treninky,
        "zapasy_data": zapasy_data,
        "graf_goly_json": graf_goly_json,
    }

    return render(request, "trener/hraci/statistiky.html", context)


#---------------------------------------------------------------------------------------------
# hrac - statistiky hrace
#---------------------------------------------------------------------------------------------
@login_required
def hrac_statistiky(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        return render(request, "error.html", {"message": "Nemáte hráčský profil."})

    tym = hrac.tym

    goly = Gol.objects.filter(hrac=hrac)
    karty = Karta.objects.filter(hrac=hrac)
    gol_count = goly.count()
    asistence_count = Gol.objects.filter(asistence=hrac).count()
    zlute = karty.filter(typ="zluta").count()
    cervene = karty.filter(typ__in=["cervena", "zluta_cervena"]).count()

    dochazka_treninky = (
        DochazkaTreninky.objects
        .filter(hrac=hrac)
        .select_related("trenink")
        .order_by("-trenink__datum")[:4]
    )

    dochazka_hrace_zapasy = (
        DochazkaZapasy.objects
        .filter(hrac=hrac, pritomen=True)
        .select_related("zapas")
        .order_by("-zapas__datum")
    )

    zapasy_data = []
    for doch in dochazka_hrace_zapasy:
        zapas = doch.zapas
        goly_hrace = zapas.goly.filter(hrac=hrac)
        asistence_hrace = zapas.goly.filter(asistence=hrac)
        karty_hrace = zapas.karty.filter(hrac=hrac)
        goly_tym = zapas.goly.filter(hrac__tym=tym).count()
        vysledek_soupere = zapas.vysledek_soupere

        zapasy_data.append({
            "zapas": zapas,
            "goly_hrace": goly_hrace,
            "asistence_hrace": asistence_hrace,
            "karty_hrace": karty_hrace,
            "vysledek_tymu": goly_tym,
            "vysledek_soupere": vysledek_soupere,
        })

    labels = []
    values = []
    for doch in dochazka_hrace_zapasy:
        zapas = doch.zapas
        pocet = zapas.goly.filter(hrac=hrac).count()
        labels.append(zapas.datum.strftime("%d.%m.%Y"))
        values.append(pocet)

    graf_goly_json = json.dumps({
        "labels": labels,
        "values": values,
    })

    zapasy_pritomen_ids = dochazka_hrace_zapasy.values_list('zapas', flat=True)
    celkove_goly = Gol.objects.filter(hrac=hrac, zapas__in=zapasy_pritomen_ids).count()
    celkove_asistence = Gol.objects.filter(asistence=hrac,
                                           zapas__in=zapasy_pritomen_ids).count()
    pocet_zapasu = len(zapasy_pritomen_ids)
    prumer_golu = round(celkove_goly / pocet_zapasu, 2) if pocet_zapasu > 0 else 0
    prumer_asistenci = round(celkove_asistence / pocet_zapasu, 2) if pocet_zapasu > 0 else 0

    context = {
        "hrac": hrac,
        "tym": tym,
        "goly": goly,
        "asistence_count": asistence_count,
        "karty": karty,
        "gol_count": gol_count,
        "zlute": zlute,
        "cervene": cervene,
        "prumer_golu": prumer_golu,
        "prumer_asistenci": prumer_asistenci,
        "graf_goly_json": graf_goly_json,
        "zapasy_data": zapasy_data,
        "dochazka_treninky": dochazka_treninky,
    }

    return render(request, "hrac/statistiky/statistiky.html", context)


# NASTAVENI


#----------------------------------------------------------------------------------------------
# nastaveni hrace
#----------------------------------------------------------------------------------------------
@login_required
def hrac_settings_view(request):
    user = request.user
    if not hasattr(user, 'hracprofile'):
        return redirect('index')

    hrac = user.hracprofile
    trener = hrac.trener
    tym = hrac.tym

    context = {
        'user': user,
        'hrac': hrac,
        'trener': trener,
        'tym': tym,
    }

    return render(request, 'hrac/nastaveni/settings.html', context)


#----------------------------------------------------------------------------------------------
# detail účtu hráče
#----------------------------------------------------------------------------------------------
@login_required
def hrac_account_view(request):
    hrac = get_object_or_404(HracProfile, user=request.user)
    trener = hrac.trener
    tym = hrac.tym

    context = {
        'hrac': hrac,
        'trener': trener,
        'tym': tym,
    }

    return render(request, 'hrac/nastaveni/account.html', context)


#----------------------------------------------------------------------------------------------
# editace profilu hrace
#----------------------------------------------------------------------------------------------
@login_required
def edit_hrac_profile(request):
    hrac = request.user.hracprofile
    if request.method == 'POST':
        form = HracProfileForm(request.POST, request.FILES, instance=hrac)
        if form.is_valid():
            form.save()
            return redirect('hrac_settings')
    else:
        form = HracProfileForm(instance=hrac)

    return render(request, 'hrac/nastaveni/edit.html', {'form': form, 'hrac': hrac})


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

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    return render(request, 'trener/nastaveni/settings.html', {
        'trener': trener,
        'tymy': tymy,
        'vybrany_tym': vybrany_tym,
    })



#----------------------------------------------------------------------------------------------
# detail uctu trenera
#----------------------------------------------------------------------------------------------
@login_required
def trener_account_view(request):
    trener = get_object_or_404(TrenerProfile, user=request.user)
    tymy = Tym.objects.filter(trener=trener)

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    return render(request, 'trener/nastaveni/account.html', {
        'trener': trener,
        'tymy': tymy,
        'vybrany_tym': vybrany_tym,
    })


#----------------------------------------------------------------------------------------------
# editace profilu trenera
#----------------------------------------------------------------------------------------------
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

    return render(request, 'trener/nastaveni/edit.html', {'form': form, 'trener': trener})



# TRENINKY


# --------------------------------------------------------------------------------
# trener - stranka pro treninky (nadcházející)
# --------------------------------------------------------------------------------
@login_required
def trener_trenink(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    tymy = Tym.objects.filter(trener=trener)

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    hraci = HracProfile.objects.filter(tym=vybrany_tym).distinct()
    now = timezone.now()

    treninky_qs = Trenink.objects.filter(
        tym=vybrany_tym,
        stav='Naplánováno'
    ).order_by('datum', 'cas').prefetch_related('dochazka', 'dochazka__hrac')

    treninky_data = []
    for trenink in treninky_qs:
        trenink_datetime = timezone.make_aware(
            datetime.combine(trenink.datum, trenink.cas),
            timezone.get_current_timezone()
        )
        if trenink_datetime < now:
            continue

        dochazka_dict = {d.hrac.id: d for d in trenink.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            dochazka_list.append(
                dochazka_dict.get(hrac.id, SimpleNamespace(hrac=hrac, pritomen=None, duvod=None))
            )

        treninky_data.append({
            'trenink': trenink,
            'dochazka_list': dochazka_list,
            'po_dohrani': trenink_datetime < now or trenink.stav != 'Naplánováno'
        })

    context = {
        'trener': trener,
        'vybrany_tym': vybrany_tym,
        'hraci': hraci,
        'treninky_data': treninky_data,
        'tymy': tymy,
    }
    return render(request, 'trener/trenink/trenink.html', context)


# ------------------------------------------------------------------------------------------------------------
# trener - historie treninku
# ------------------------------------------------------------------------------------------------------------
@login_required
def trener_trenink_historie(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    tymy = Tym.objects.filter(trener=trener)

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    hraci = HracProfile.objects.filter(tym=vybrany_tym).distinct()
    now = timezone.now()

    treninky_qs = Trenink.objects.filter(
        tym=vybrany_tym
    ).prefetch_related('dochazka', 'dochazka__hrac') \
     .order_by('-datum', '-cas')

    treninky_data = []
    for trenink in treninky_qs:
        trenink_datetime = timezone.make_aware(
            datetime.combine(trenink.datum, trenink.cas),
            timezone.get_current_timezone()
        )
        if trenink_datetime >= now and trenink.stav == 'Naplánováno':
            continue

        dochazka_dict = {d.hrac.id: d for d in trenink.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            dochazka_list.append(
                dochazka_dict.get(hrac.id, SimpleNamespace(hrac=hrac, pritomen=None, duvod=None))
            )

        treninky_data.append({'trenink': trenink, 'dochazka_list': dochazka_list})

    context = {
        'trener': trener,
        'vybrany_tym': vybrany_tym,
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
    vybrany_tym = request.session.get("selected_tym")
    if vybrany_tym:
        vybrany_tym = Tym.objects.filter(id=vybrany_tym, trener=trener).first()
    else:
        vybrany_tym = tymy.first()

    if request.method == 'POST':
        form = TreninkForm(request.POST)
        if form.is_valid():
            trenink = form.save(commit=False)
            trenink.tym = vybrany_tym
            trenink.save()
            messages.success(request, 'Trénink byl úspěšně přidán.')
            return redirect('trener_trenink')
    else:
        form = TreninkForm()

    return render(request, 'trener/trenink/add.html', {'form': form, 'tymy': tymy})




#----------------------------------------------------------------------------------------------------------------
# uprava treninku
#----------------------------------------------------------------------------------------------------------------
@login_required
def edit_trenink_view(request, trenink_id):
    trener = request.user.trenerprofile
    trenink = get_object_or_404(Trenink, id=trenink_id, tym__trener=trener)

    if request.method == 'POST':
        form = TreninkForm(request.POST, instance=trenink)
        if form.is_valid():
            form.save()
            messages.success(request, "Trénink byl aktualizován.")
            return redirect('trener_trenink')
    else:
        form = TreninkForm(instance=trenink)

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


#----------------------------------------------------------------------------------------------
# hrac - stranka pro treninky
#----------------------------------------------------------------------------------------------
@login_required
def hrac_trenink(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        return render(request, 'index.html', {'message': 'Profil hráče nebyl nalezen.'})

    now = timezone.localtime(timezone.now())

    treninky = Trenink.objects.filter(
        tym=hrac.tym,
        stav='Naplánováno'
    ).order_by('datum', 'cas')

    treninky_data = []
    for trenink in treninky:
        trenink_datetime = timezone.make_aware(datetime.combine(trenink.datum, trenink.cas))
        if trenink_datetime < now:
            continue

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
        'tym': hrac.tym,
    })


#----------------------------------------------------------------------------------------------
# hrac - historie treninku
#----------------------------------------------------------------------------------------------
@login_required
def hrac_trenink_historie(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        return render(request, 'index.html', {'message': 'Profil hráče nebyl nalezen.'})

    now = timezone.localtime(timezone.now())

    treninky = Trenink.objects.filter(tym=hrac.tym).order_by('-datum', '-cas')

    treninky_data = []
    for trenink in treninky:
        trenink_datetime = timezone.make_aware(datetime.combine(trenink.datum, trenink.cas))
        if trenink_datetime >= now:
            continue

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
        'tym': hrac.tym,
    })


#----------------------------------------------------------------------------------------------
# hlasovani pro hrace o treninku
#----------------------------------------------------------------------------------------------
@login_required
def hlasovani_dochazka_view(request, trenink_id):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte hráčský profil.")
        return redirect('index')

    trenink = get_object_or_404(
        Trenink,
        id=trenink_id,
        tym=hrac.tym
    )

    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        pritomen_raw = request.POST.get('pritomen')
        if pritomen_raw not in ('true', 'false'):
            messages.error(request, "Neplatná volba.")
            return redirect(zpet)

        pritomen = (pritomen_raw == 'true')
        duvod = request.POST.get('duvod', '').strip() or None

        DochazkaTreninky.objects.update_or_create(
            trenink=trenink,
            hrac=hrac,
            defaults={'pritomen': pritomen, 'duvod': duvod}
        )

        messages.success(request, "Tvá docházka byla uložena.")
        return redirect(zpet)

    return redirect(zpet)


#----------------------------------------------------------------------------------------------
# zrusit hlasovani na trenink
#----------------------------------------------------------------------------------------------
@login_required
def hlasovani_dochazka_smazat(request, trenink_id):
    hrac = request.user.hracprofile
    trenink = get_object_or_404(
        Trenink,
        id=trenink_id,
        tym=hrac.tym
    )

    zpet = request.META.get('HTTP_REFERER', '/')

    dochazka_obj = DochazkaTreninky.objects.filter(trenink=trenink, hrac=hrac).first()
    if dochazka_obj:
        dochazka_obj.pritomen = None
        dochazka_obj.duvod = ''
        dochazka_obj.save()
        messages.success(request, "Volba byla odstraněna.")

    return redirect(zpet)



# ZAPASY

#----------------------------------------------------------------------------------------------
# hrac - stranka pro zapasy
#----------------------------------------------------------------------------------------------
@login_required
def hrac_zapas(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte profil.")
        return redirect('index')

    tym = hrac.tym
    now = timezone.localtime()

    zapasy = (
        Zapas.objects.filter(tym=tym, stav='Naplánováno')
        .filter(datum__gte=now.date())
        .order_by('datum', 'cas')
        .prefetch_related('dochazka')
    )

    zapasy_data = []
    for zapas in zapasy:
        datetime_zapasu = timezone.make_aware(
            datetime.combine(zapas.datum, zapas.cas),
            timezone.get_current_timezone()
        )

        if datetime_zapasu <= now:
            continue

        dochazka_obj = zapas.dochazka.filter(hrac=hrac).first()

        zapasy_data.append({
            'zapas': zapas,
            'dochazka': dochazka_obj,
            'klub': tym.nazev,
            'hlasoval': dochazka_obj.pritomen is not None if dochazka_obj else False,
            'po_dohrani': (
                datetime_zapasu < now and
                (zapas.vysledek_tymu is None or zapas.vysledek_soupere is None)
            )
        })

    return render(request, 'hrac/zapas/zapas.html', {
        'hrac': hrac,
        'tym': tym,
        'trener': tym.trener,
        'zapasy_data': zapasy_data
    })


#----------------------------------------------------------------------------------------------
# hlasovani pro hrace o zapasu
#----------------------------------------------------------------------------------------------
@login_required
def hrac_hlasovani_zapas(request, zapas_id):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte hráčský profil.")
        return redirect('index')

    zapas = get_object_or_404(Zapas, id=zapas_id, tym=hrac.tym)
    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        pritomen_raw = request.POST.get('pritomen')
        if pritomen_raw not in ('true', 'false'):
            messages.error(request, "Neplatná volba.")
            return redirect(zpet)

        pritomen = pritomen_raw == 'true'

        DochazkaZapasy.objects.update_or_create(
            zapas=zapas,
            hrac=hrac,
            defaults={'pritomen': pritomen}
        )

        messages.success(request, "Tvá účast byla zaznamenána.")
        return redirect(zpet)

    return redirect(zpet)


#----------------------------------------------------------------------------------------------
# zrusit hlasovani na zapas
#----------------------------------------------------------------------------------------------
@login_required
def hrac_hlasovani_zapas_smazat(request, zapas_id):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte hráčský profil.")
        return redirect('index')

    zapas = get_object_or_404(Zapas, id=zapas_id, tym=hrac.tym)

    dochazka = zapas.dochazka.filter(hrac=hrac).first()
    zpet = request.META.get('HTTP_REFERER', '/')

    if dochazka:
        dochazka.pritomen = None
        dochazka.save()
        messages.success(request, "Volba byla zrušena.")

    return redirect(zpet)


#----------------------------------------------------------------------------------------------
# trener - stranka pro zapasy
#----------------------------------------------------------------------------------------------
@login_required
def trener_zapas(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    tymy = trener.tymy.all()

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    vybrany_tym = tymy.filter(id=selected_tym_id).first() if selected_tym_id else tymy.first()
    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    hraci = HracProfile.objects.filter(tym=vybrany_tym).distinct()

    now = timezone.now()

    zapasy_qs = (
        Zapas.objects.filter(tym=vybrany_tym, stav='Naplánováno')
                     .prefetch_related('dochazka', 'dochazka__hrac')
                     .order_by('datum', 'cas')
    )

    zapasy_data = []
    for zapas in zapasy_qs:
        dochazka_dict = {d.hrac.id: d for d in zapas.dochazka.all()}
        dochazka_list = [
            dochazka_dict.get(hrac.id, SimpleNamespace(hrac=hrac, pritomen=None, poznamka=None))
            for hrac in hraci
        ]

        zapas_datetime = timezone.make_aware(
            datetime.combine(zapas.datum, zapas.cas),
            timezone.get_current_timezone()
        )

        po_dohrani = zapas_datetime < now

        zapasy_data.append({
            'zapas': zapas,
            'dochazka_list': dochazka_list,
            'po_dohrani': po_dohrani,
        })

    context = {
        'trener': trener,
        'vybrany_tym': vybrany_tym,
        'hraci': hraci,
        'zapasy_data': zapasy_data,
        'tymy': tymy,
    }

    return render(request, 'trener/zapas/zapas.html', context)


#----------------------------------------------------------------------------------------------
# pridani zapasu
#----------------------------------------------------------------------------------------------
@login_required
def add_zapas_view(request):
    if not hasattr(request.user, 'trenerprofile'):
        return redirect('index')

    trener = request.user.trenerprofile
    tymy = Tym.objects.filter(trener=trener)

    vybrany_tym_id = request.session.get("selected_tym")
    if vybrany_tym_id:
        vybrany_tym = Tym.objects.filter(id=vybrany_tym_id, trener=trener).first()
    else:
        vybrany_tym = tymy.first()

    if request.method == 'POST':
        form = ZapasForm(request.POST)
        if form.is_valid():
            zapas = form.save(commit=False)
            zapas.tym = vybrany_tym
            zapas.trener = trener
            zapas.save()
            messages.success(request, 'Zápas byl úspěšně přidán.')
            return redirect('trener_zapas')
    else:
        form = ZapasForm()

    return render(request, 'trener/zapas/add.html', {
        'form': form,
        'tymy': tymy
    })


#----------------------------------------------------------------------------------------------
# upraveni zapasu
#----------------------------------------------------------------------------------------------
@login_required
def edit_zapas_view(request, zapas_id):
    trener = getattr(request.user, 'trenerprofile', None)
    if not trener:
        return redirect('index')

    zapas = get_object_or_404(Zapas, id=zapas_id, tym__in=trener.tymy.all())

    selected_tym_id = request.session.get("selected_tym")
    vybrany_tym = trener.tymy.filter(id=selected_tym_id).first() if selected_tym_id else trener.tymy.first()
    if vybrany_tym not in trener.tymy.all():
        vybrany_tym = trener.tymy.first()

    if request.method == 'POST':
        form = ZapasForm(request.POST, instance=zapas)
        if form.is_valid():
            zapas = form.save(commit=False)
            zapas.tym = vybrany_tym
            zapas.save()
            messages.success(request, "Zápas byl aktualizován.")
            return redirect('trener_zapas')
    else:
        form = ZapasForm(instance=zapas)

    context = {
        'form': form,
        'edit': True,
        'vybrany_tym': vybrany_tym,
        'tymy': trener.tymy.all(),
    }

    return render(request, 'trener/zapas/edit.html', context)


#----------------------------------------------------------------------------------------------
# smazani zapasu
#----------------------------------------------------------------------------------------------
@login_required
def delete_zapas_view(request, zapas_id):
    trener = getattr(request.user, 'trenerprofile', None)
    if not trener:
        return redirect('index')

    zapas = get_object_or_404(Zapas, id=zapas_id, tym__in=trener.tymy.all())
    zpet = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        zapas.delete()
        messages.success(request, "Zápas byl úspěšně smazán.")

        selected_tym_id = request.session.get("selected_tym")
        if selected_tym_id:
            return redirect(f"{zpet}?selected_tym={selected_tym_id}")

        return redirect(zpet)

    return redirect(zpet)



#----------------------------------------------------------------------------------------------
# oznaceni zapasu jako odehrany
#----------------------------------------------------------------------------------------------
@login_required
def oznacit_dohrano_view(request, zapas_id):
    trener = getattr(request.user, 'trenerprofile', None)
    if not trener:
        return redirect('index')

    tymy = trener.tymy.all()
    selected_tym_id = request.session.get("selected_tym")
    vybrany_tym = tymy.filter(id=selected_tym_id).first() if selected_tym_id else tymy.first()

    zapas = get_object_or_404(Zapas, id=zapas_id, tym=vybrany_tym)

    if request.method == 'POST':
        form = DohranyZapasForm(request.POST, instance=zapas)

        if form.is_valid():
            zapas = form.save(commit=False)

            zapas.vysledek_tymu = request.POST.get("vysledek_tymu")
            zapas.vysledek_soupere = request.POST.get("vysledek_soupere")
            zapas.stav = "Dohráno"
            zapas.save()

            # Goly
            zapas.goly.all().delete()
            pocet_golu = int(request.POST.get("pocet_golu", 0))

            for i in range(1, pocet_golu + 1):
                hrac_id = request.POST.get(f"gol_hrac_{i}")
                minuta = request.POST.get(f"gol_minuta_{i}")
                typ_form = request.POST.get(f"gol_typ_{i}")
                asistence_id = request.POST.get(f"gol_asistent_{i}") or None

                if not hrac_id or not minuta:
                    continue

                if asistence_id and asistence_id == str(hrac_id):
                    asistence_id = None

                typ = "normalni" if asistence_id else (typ_form or "normalni")

                Gol.objects.create(
                    zapas=zapas,
                    hrac_id=hrac_id,
                    minuta=int(minuta),
                    typ=typ,
                    asistence_id=asistence_id
                )

            zapas.karty.all().delete()
            pocet_karet = int(request.POST.get("pocet_karet", 0))

            hraci_karty = {}

            for i in range(1, pocet_karet + 1):
                hrac_id = request.POST.get(f"karta_hrac_{i}")
                minuta = request.POST.get(f"karta_minuta_{i}")
                typ = request.POST.get(f"karta_typ_{i}")

                if hrac_id and minuta and typ:
                    hraci_karty.setdefault(hrac_id, []).append({
                        "typ": typ,
                        "minuta": int(minuta)
                    })

            for hrac_id, karty_list in hraci_karty.items():
                karty_list.sort(key=lambda x: x["minuta"])

                zlute = [k for k in karty_list if k["typ"] == "zluta"]

                if len(zlute) >= 2:
                    for k in karty_list:
                        if k["typ"] == "zluta" and k != zlute[0]:
                            k["typ"] = "cervena_ze_zlutych"

                for karta in karty_list:
                    Karta.objects.create(
                        zapas=zapas,
                        hrac_id=hrac_id,
                        minuta=karta["minuta"],
                        typ=karta["typ"]
                    )

            messages.success(request, "Zápas byl uložen včetně gólů, asistencí a karet.")
            return redirect('trener_zapas')

    else:
        form = DohranyZapasForm(instance=zapas)

    hraci = HracProfile.objects.filter(
        dochazkazapasy__zapas=zapas,
        dochazkazapasy__pritomen=True
    )

    context = {
        "form": form,
        "zapas": zapas,
        "vybrany_tym": vybrany_tym,
        "tymy": tymy,
        "hraci": hraci,
    }
    return render(request, "trener/zapas/oznacit_dohrano.html", context)




#----------------------------------------------------------------------------------------------
# trener - odehrany zapasy
#----------------------------------------------------------------------------------------------
@login_required
def trener_dohrane_zapasy(request):
    try:
        trener = request.user.trenerprofile
    except TrenerProfile.DoesNotExist:
        return render(request, 'error.html', {'message': 'Profil trenéra nebyl nalezen.'})

    tymy = trener.tymy.all()

    selected_tym_id = request.GET.get("selected_tym")
    if selected_tym_id:
        request.session["selected_tym"] = selected_tym_id

    selected_tym_id = request.session.get("selected_tym")
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    if vybrany_tym not in tymy:
        vybrany_tym = tymy.first()

    hraci = HracProfile.objects.filter(tym=vybrany_tym).distinct()

    zapasy_qs = (
        Zapas.objects.filter(tym=vybrany_tym, stav='Dohráno')
                     .prefetch_related(
                        'dochazka', 'dochazka__hrac',
                        'goly', 'goly__hrac',
                        'karty', 'karty__hrac'
                     )
                     .order_by('-datum', '-cas')
    )

    zapasy_data = []

    for zapas in zapasy_qs:

        dochazka_dict = {d.hrac.id: d for d in zapas.dochazka.all()}
        dochazka_list = []
        for hrac in hraci:
            dochazka_list.append(
                dochazka_dict.get(hrac.id, SimpleNamespace(
                    hrac=hrac,
                    pritomen=None,
                    poznamka=None
                ))
            )

        goly = zapas.goly.all()

        goly_tym = goly.filter(hrac__tym=vybrany_tym)
        vt = goly_tym.count()
        vs = zapas.vysledek_soupere

        karty = zapas.karty.all()

        zlute = karty.filter(
            hrac__tym=vybrany_tym,
            typ="zluta"
        ).count()

        cervene = karty.filter(
            hrac__tym=vybrany_tym,
            typ="cervena"
        ).count()

        zapasy_data.append({
            'zapas': zapas,
            'dochazka_list': dochazka_list,
            'goly': goly,
            'vt': vt,
            'vs': vs,
            'karty': karty,
            'zlute': zlute,
            'cervene': cervene,
        })

    context = {
        'trener': trener,
        'vybrany_tym': vybrany_tym,
        'hraci': hraci,
        'zapasy_data': zapasy_data,
        'tymy': tymy,
    }

    return render(request, 'trener/zapas/zapas_dohrano.html', context)


#----------------------------------------------------------------------------------------------
# hrac - dohrane zapasy
#----------------------------------------------------------------------------------------------
@login_required
def hrac_dohrane_zapasy(request):
    try:
        hrac = request.user.hracprofile
    except HracProfile.DoesNotExist:
        messages.error(request, "Nemáte hráčský profil.")
        return redirect('index')

    dnes = timezone.localdate()
    tym = hrac.tym

    zapasy = Zapas.objects.filter(
        tym=tym
    ).filter(
        Q(stav='Dohráno') |
        Q(stav='Naplánováno', datum__lt=dnes)
    ).prefetch_related('goly', 'goly__hrac', 'karty', 'karty__hrac', 'dochazka').order_by('-datum', '-cas')

    zapasy_data = []

    for zapas in zapasy:

        dochazka_obj = zapas.dochazka.filter(hrac=hrac).first()

        goly = zapas.goly.all()
        goly_tym = goly.filter(hrac__tym=tym)

        goly_souper = goly.exclude(hrac__tym=tym)
        vysledek_tymu = goly_tym.count()

        vysledek_soupere = zapas.vysledek_soupere

        karty = zapas.karty.all()
        karty_tym = karty.filter(hrac__tym=tym)
        karty_souper = karty.exclude(hrac__tym=tym)

        zapasy_data.append({
            'zapas': zapas,
            'dochazka': dochazka_obj,
            'vysledek_tymu': vysledek_tymu,
            'vysledek_soupere': vysledek_soupere,
            'goly': goly,
            'goly_tym': goly_tym,
            'goly_souper': goly_souper,
            'karty': karty,
            'karty_tym': karty_tym,
            'karty_souper': karty_souper,
        })

    context = {
        'hrac': hrac,
        'tym': tym,
        'zapasy_data': zapasy_data,
    }

    return render(request, 'hrac/zapas/zapas_dohrano.html', context)



#----------------------------------------------------------------------------------------------
# trener - detail zapasu
#----------------------------------------------------------------------------------------------
@login_required
def trener_zapas_detail(request, zapas_id):
    zapas = get_object_or_404(Zapas, id=zapas_id)

    hrac = getattr(request.user, "hracprofile", None)
    trener = getattr(request.user, "trenerprofile", None)

    vybrany_tym_id = request.session.get("selected_tym")
    vybrany_tym = None

    if hrac:
        vybrany_tym = hrac.tym
    elif trener and vybrany_tym_id:
        vybrany_tym = trener.tymy.filter(id=vybrany_tym_id).first()
    elif trener:
        vybrany_tym = trener.tymy.first()

    if vybrany_tym is None:
        raise Http404("Nemáte přiřazený tým nebo nevybrali jste tým.")

    if zapas.tym != vybrany_tym:
        raise Http404("Tento zápas nepatří do vybraného týmu.")

    hraci = HracProfile.objects.filter(tym=vybrany_tym).order_by('user__first_name', 'user__last_name')

    dochazka_dict = {d.hrac.id: d for d in zapas.dochazka.all()}

    dochazka_list = [
        dochazka_dict.get(
            hrac.id,
            SimpleNamespace(hrac=hrac, pritomen=None, poznamka=None)
        )
        for hrac in hraci
    ]

    pocet_hracu = len(dochazka_list)
    pocet_pritomnych = sum(1 for d in dochazka_list if d.pritomen)
    procento_pritomnych = round((pocet_pritomnych / pocet_hracu) * 100, 1) if pocet_hracu > 0 else 0.0

    context = {
        'zapas': zapas,
        'vybrany_tym': vybrany_tym,
        'hrac': hrac,
        'dochazka_list': dochazka_list,
        'trener': trener,
        'procento_pritomnych': procento_pritomnych,
    }

    return render(request, 'trener/zapas/detail.html', context)



#----------------------------------------------------------------------------------------------
# trener - detail treninku
#----------------------------------------------------------------------------------------------
@login_required
def trener_trenink_detail(request, trenink_id):
    trenink = get_object_or_404(Trenink, id=trenink_id)

    hrac = getattr(request.user, "hracprofile", None)
    trener = getattr(request.user, "trenerprofile", None)

    vybrany_tym_id = request.session.get("selected_tym")
    vybrany_tym = None

    if hrac:
        vybrany_tym = hrac.tym
    elif trener and vybrany_tym_id:
        vybrany_tym = trener.tymy.filter(id=vybrany_tym_id).first()
    elif trener:
        vybrany_tym = trener.tymy.first()

    if vybrany_tym is None:
        raise Http404("Nemáte přiřazený tým nebo nevybrali jste tým.")

    if trenink.tym != vybrany_tym:
        raise Http404("Tento trénink nepatří do vybraného týmu.")

    hraci = HracProfile.objects.filter(tym=vybrany_tym).order_by('user__first_name', 'user__last_name')

    dochazka_dict = {d.hrac.id: d for d in trenink.dochazka.all()}

    dochazka_list = [
        dochazka_dict.get(
            hrac.id,
            SimpleNamespace(hrac=hrac, pritomen=None, duvod=None)
        )
        for hrac in hraci
    ]

    pocet_hracu = len(dochazka_list)
    pocet_pritomnych = sum(1 for d in dochazka_list if d.pritomen)
    procento_pritomnych = round((pocet_pritomnych / pocet_hracu) * 100, 1) if pocet_hracu > 0 else 0.0

    context = {
        'trenink': trenink,
        'vybrany_tym': vybrany_tym,
        'hrac': hrac,
        'dochazka_list': dochazka_list,
        'trener': trener,
        'procento_pritomnych': procento_pritomnych,
    }

    return render(request, 'trener/trenink/detail.html', context)



#----------------------------------------------------------------------------------------------
# trener - tym
#----------------------------------------------------------------------------------------------
@login_required
def trener_tym(request):

    hrac = getattr(request.user, "hracprofile", None)
    trener = getattr(request.user, "trenerprofile", None)

    vybrany_tym_id = request.session.get("selected_tym")
    vybrany_tym = None

    if hrac:
        vybrany_tym = hrac.tym
    elif trener and vybrany_tym_id:
        vybrany_tym = trener.tymy.filter(id=vybrany_tym_id).first()
    elif trener:
        vybrany_tym = trener.tymy.first()

    if vybrany_tym is None:
        raise Http404("Nemáte přiřazený tým nebo jste nevybrali tým.")

    hraci = (
        HracProfile.objects.filter(tym=vybrany_tym)
        .order_by("user__first_name", "user__last_name")
    )

    dnes = now().date()

    treninky = Trenink.objects.filter(
        tym=vybrany_tym,
        datum__lt=dnes
    )

    zapasy = Zapas.objects.filter(
        tym=vybrany_tym,
        datum__lt=dnes
    )

    hraci_data = []

    for h in hraci:

        tren_total = treninky.count()

        tren_yes = (
            DochazkaTreninky.objects
            .filter(hrac=h, trenink__in=treninky, pritomen=True)
            .count()
        )

        tren_percent = round((tren_yes / tren_total) * 100, 1) if tren_total > 0 else 0

        zap_total = zapasy.count()

        zap_yes = (
            DochazkaZapasy.objects
            .filter(hrac=h, zapas__in=zapasy, pritomen=True)
            .count()
        )

        zap_percent = round((zap_yes / zap_total) * 100, 1) if zap_total > 0 else 0

        asistence = Gol.objects.filter(asistence=h).count()
        goly = Gol.objects.filter(hrac=h).count()
        zlute = Karta.objects.filter(hrac=h, typ="zluta").count()
        cervene = Karta.objects.filter(hrac=h, typ__in=["cervena", "zluta_cervena"]).count()

        hraci_data.append({
            "hrac": h,
            "treninky_percent": tren_percent,
            "zapasy_percent": zap_percent,
            "goly": goly,
            "zlute": zlute,
            "cervene": cervene,
            "asistence": asistence,
        })

    hraci_data = sorted(
        hraci_data,
        key=lambda x: (
            -x["goly"],
            -x["asistence"],
            -x["zapasy_percent"],
            x["hrac"].user.last_name,
            x["hrac"].user.first_name,
        )
    )

    tym_goly = Gol.objects.filter(
        hrac__tym=vybrany_tym,
        zapas__in=zapasy
    ).count()

    vyhry = 0
    prohry = 0
    remizy = 0

    for z in zapasy:
        goly_tym = z.goly.filter(hrac__tym=vybrany_tym).count()
        goly_souper = z.vysledek_soupere

        if goly_tym > goly_souper:
            vyhry += 1
        elif goly_tym < goly_souper:
            prohry += 1
        else:
            remizy += 1

    context = {
        "vybrany_tym": vybrany_tym,
        "hraci_data": hraci_data,
        "hrac": hrac,
        "trener": trener,
        "tym_goly": tym_goly,
        "vyhry": vyhry,
        "prohry": prohry,
        "remizy": remizy,
        "asistence": asistence,
    }

    return render(request, "trener/tym/tym.html", context)
