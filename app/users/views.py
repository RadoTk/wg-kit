import logging
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.db import transaction
from .forms import UserForm, UserProfileForm
from django.contrib.auth.forms import UserCreationForm

logger = logging.getLogger(__name__)


class UserLoginView(LoginView):
    """Vue de connexion personnalisée."""
    template_name = "users/login.html"
    



@login_required
def profile_edit(request):
    """Permet à un utilisateur connecté de modifier ses informations."""
    user = request.user

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user_form.save()
                    profile_form.save()

                messages.success(request, "Votre profil a été mis à jour avec succès.")
                return redirect("users:profile_edit")

            except Exception as e:
                logger.error(f"Erreur update profil: {str(e)}")
                messages.error(request, "Une erreur est survenue. Merci de réessayer.")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user.profile)

    return render(request, "users/profile_edit.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })


def user_logout(request):
    """Déconnecte l'utilisateur."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect("users:login")


def signup(request):
    """
    Inscription d’un nouvel utilisateur.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()

                messages.success(request, "Votre compte a été créé avec succès !")
                return redirect("users:login")

            except Exception as e:
                logger.error(f"Erreur inscription: {str(e)}")
                messages.error(request, "Une erreur est survenue lors de l’inscription.")
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = UserCreationForm()

    return render(request, "users/signup.html", {"form": form})
