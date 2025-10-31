from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls.base import reverse_lazy

from . import views

urlpatterns = [
    path('', views.index, name='index'),

# login
    path('prihlaseni/', views.login_view, name='login'),
    path('prihlaseni/udaje/', views.first_login_view, name='first_login_view'),
    path('odhlaseni/', views.logout_view, name='logout'),

# dashboard
    path('trener/', views.trener_dashboard, name='trener_dashboard'),
    path('hrac/', views.hrac_dashboard, name='hrac_dashboard'),

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
             template_name='trener/password_change.html',
             success_url=reverse_lazy('trener_password_change_done')
         ),
         name='trener_password_change'),
    path('trener/nastaveni/zmena-hesla/zmeneno/',
         auth_views.PasswordChangeDoneView.as_view(template_name='trener/password_change_done.html'),
         name='trener_password_change_done'),

# zmena hesla hrac
    path('hrac/nastaveni/zmena-hesla/',
         auth_views.PasswordChangeView.as_view(
             template_name='hrac/password_change.html',
             success_url=reverse_lazy('hrac_password_change_done')
         ),
         name='hrac_password_change'),
    path('hrac/nastaveni/zmena-hesla/zmeneno/',
         auth_views.PasswordChangeDoneView.as_view(template_name='hrac/password_change_done.html'),
         name='hrac_password_change_done'),
]
