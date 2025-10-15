from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('register/hrac/<int:user_id>/', views.register_hrac, name='register_hrac'),
    path('register/trener/<int:user_id>/', views.register_trener, name='register_trener'),
    path('logout/', views.logout_view, name='logout'),
    path('hrac/', views.hrac_dashboard, name='hrac_dashboard'),
    path('trener/', views.trener_dashboard, name='trener_dashboard'),
]