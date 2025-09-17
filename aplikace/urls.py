from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('hrac/', views.hrac_view, name='hrac'),
    path('trener/', views.trener_view, name='trener'),
]