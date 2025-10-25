from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('first-login/', views.first_login_view, name='first_login_view'),
    path('logout/', views.logout_view, name='logout'),
    path('hrac/', views.hrac_dashboard, name='hrac_dashboard'),
    path('trener/', views.trener_dashboard, name='trener_dashboard'),
]
