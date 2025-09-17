from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .models import Profile


# Create your views here.
def index(request):
    context = {
    }
    return render(request, 'index.html', context=context)


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_superuser:
                return redirect('/admin/')

            try:
                role = user.profile.role
            except Profile.DoesNotExist:
                role = 'hrac'

            if role == 'hrac':
                return redirect('/squadra/hrac/')
            elif role == 'trener':
                return redirect('/squadra/trener/')

        return render(request, "login/login.html", {"form": form})

    else:
        form = AuthenticationForm()
        return render(request, "login/login.html", {"form": form})

@login_required
def hrac_view(request):
    return render(request, "hrac/hrac.html")

@login_required
def trener_view(request):
    return render(request, "trener/trener.html")