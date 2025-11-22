from django.conf import settings
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls.base import reverse_lazy

from squadra.settings import BASE_DIR
from . import views
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),

# login
    path('prihlaseni/', views.login_view, name='login'),
    path('prihlaseni/udaje/', views.first_login_view, name='first_login_view'),
    path('odhlaseni/', views.logout_view, name='logout'),

# dashboard
    path('trener/', views.trener_dashboard, name='trener_dashboard'),
    path('hrac/', views.hrac_dashboard, name='hrac_dashboard'),

# trener - hraci
    path('trener/hraci', views.trener_hraci_view, name='trener_hraci'),

# settings
    path('trener/nastaveni/', views.trener_settings_view, name='trener_settings'),
    path('hrac/nastaveni/', views.hrac_settings_view, name='hrac_settings'),

# account
    path('trener/nastaveni/ucet/', views.trener_account_view, name='trener_account'),
    path('hrac/nastaveni/ucet/', views.hrac_account_view, name='hrac_account'),

# edit
    path('trener/nastaveni/upravit-profil/', views.edit_trener_profile, name='edit_trener_profile'),
    path('hrac/nastaveni/upravit-profil/', views.edit_hrac_profile, name='edit_hrac_profile'),

# zmena hesla trener
    path('trener/nastaveni/zmena-hesla/',
         auth_views.PasswordChangeView.as_view(
             template_name='trener/heslo/password_change.html',
             success_url=reverse_lazy('trener_password_change_done')
         ),
         name='trener_password_change'),
    path('trener/nastaveni/zmena-hesla/zmeneno/',
         auth_views.PasswordChangeDoneView.as_view(template_name='trener/heslo/password_change_done.html'),
         name='trener_password_change_done'),

# zmena hesla hrac
    path('hrac/nastaveni/zmena-hesla/',
         auth_views.PasswordChangeView.as_view(
             template_name='hrac/heslo/password_change.html',
             success_url=reverse_lazy('hrac_password_change_done')
         ),
         name='hrac_password_change'),
    path('hrac/nastaveni/zmena-hesla/zmeneno/',
         auth_views.PasswordChangeDoneView.as_view(template_name='hrac/heslo/password_change_done.html'),
         name='hrac_password_change_done'),



# TRENINKY

    # hrac - stranka treninku
    path('hrac/treninky/', views.hrac_trenink, name='hrac_trenink'),

    # hrac - historie treninku
    path('hrac/treninky/historie/', views.hrac_trenink_historie, name='hrac_trenink_historie'),

    # trener - stranka treninku
    path('trener/treninky/', views.trener_trenink, name='trener_trenink'),

    # trener - historie treninku
    path('trener/treninky/historie/', views.trener_trenink_historie, name='trener_trenink_historie'),

    # pridani treninku
    path('trener/treninky/pridat/', views.add_trenink_view, name='add_trenink'),

    # uprava treninku
    path('trener/treninky/upravit-trenink/<int:trenink_id>/', views.edit_trenink_view, name='edit_trenink'),

    # smazani treninku
    path('trener/treninky/smazat-trenink/<int:trenink_id>/', views.delete_trenink_view, name='delete_trenink'),

    # hlasovani na trenink
    path('hrac/treninky/hlasovani/<int:trenink_id>/', views.hlasovani_dochazka_view, name='hlasovani_dochazka'),

    # hlasovani na trenink - smazat
    path('hrac/treninky/hlasovani/smazat/<int:trenink_id>/', views.hlasovani_dochazka_smazat, name='hlasovani_dochazka_smazat'),



# ZAPASY

    # hrac - stranka zapasu
    path('hrac/zapasy/', views.hrac_zapas, name='hrac_zapas'),

    # trener - stranka zapasu
    path('trener/zapasy/', views.trener_zapas, name='trener_zapas'),

    # hlasovani na zapas
    path('hrac/zapasy/hlasovani/<int:zapas_id>/', views.hrac_hlasovani_zapas, name='hrac_hlasovani_zapas'),

    # hlasovani na zapas - smazat
    path('hrac/zapasy/hlasovani/smazat/<int:zapas_id>/', views.hrac_hlasovani_zapas_smazat, name='hrac_hlasovani_zapas_smazat'),

    # pridani zapasu
    path('trener/zapasy/pridat/', views.add_zapas_view, name='add_zapas'),

    # uprava zapasu
    path('trener/zapasy/upravit/<int:zapas_id>/', views.edit_zapas_view, name='edit_zapas'),

    # smazani zapasu
    path('trener/zapasy/smazat/<int:zapas_id>/', views.delete_zapas_view, name='delete_zapas'),

    # oznacit zapas jako dohrany
    path('trener/zapasy/oznacit_dohrano/<int:zapas_id>/', views.oznacit_dohrano_view, name='oznacit_dohrano'),

    # trener - odehrane zapasy
    path('trener/zapasy/odehrane-zapasy/', views.trener_dohrane_zapasy, name='trener_dohrane_zapasy'),

    # hrac - odehrane zapasy
    path('hrac/zapasy/odehrane-zapasy/', views.hrac_dohrane_zapasy, name='hrac_dohrane_zapasy'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=BASE_DIR / 'static')
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
