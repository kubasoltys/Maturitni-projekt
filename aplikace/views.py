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
            'klub': tym.club,
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
                dochazka_dict.get(hrac.id, SimpleNamespace(hrac=hrac, pritomen=None, duvod=None))
            )

        treninky_data.append({
            'trenink': trenink,
            'dochazka_list': dochazka_list,
            'po_dohrani': trenink_datetime < now or trenink.stav != 'Naplánováno'
        })

    zapasy_qs = (
        Zapas.objects.filter(
            tym=vybrany_tym,
            datum__gte=date.today()
        )
        .prefetch_related('dochazka', 'dochazka__hrac')
        .order_by('datum', 'cas')[:1]
    )

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
    if selected_tym_id:
        vybrany_tym = tymy.filter(id=selected_tym_id).first()
    else:
        vybrany_tym = tymy.first()

    zapas = get_object_or_404(Zapas, id=zapas_id, tym=vybrany_tym)

    if request.method == 'POST':
        form = DohranyZapasForm(request.POST, instance=zapas)
        if form.is_valid():
            zapas = form.save(commit=False)
            zapas.stav = 'Dohráno'
            zapas.save()
            return redirect('trener_zapas')
    else:
        form = DohranyZapasForm(instance=zapas)

    context = {
        'form': form,
        'zapas': zapas,
        'vybrany_tym': vybrany_tym,
        'tymy': tymy,
    }

    return render(request, 'trener/zapas/oznacit_dohrano.html', context)


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
                     .prefetch_related('dochazka', 'dochazka__hrac')
                     .order_by('datum', 'cas')
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

        zapasy_data.append({
            'zapas': zapas,
            'dochazka_list': dochazka_list,
        })

    context = {
        'trener': trener,
        'vybrany_tym': vybrany_tym,
        'hraci': hraci,
        'zapasy_data': zapasy_data,
        'tymy': tymy,
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