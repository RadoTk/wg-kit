import logging
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

from .forms import SignupForm, UserForm, UserProfileForm, AddressForm, Address

logger = logging.getLogger(__name__)

# -------------------------
# AUTHENTIFICATION
# -------------------------

class UserLoginView(LoginView):
    """Vue de connexion personnalisée."""
    template_name = "users/login.html"


def user_logout(request):
    """Déconnexion utilisateur."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect("users:login")


def signup(request):
    """
    Inscription utilisateur + création profil + adresse principale.
    """
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

                messages.success(request, "Votre compte a été créé avec succès !")
                return redirect("users:login")

            except Exception as e:
                logger.error(f"[Signup] Erreur lors de l'inscription : {e}")
                messages.error(request, f"Une erreur interne est survenue : {e}")

        else:
            # Affiche toutes les erreurs champ par champ
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans « {field} » : {error}")

    else:
        form = SignupForm()

    return render(request, "users/signup.html", {"form": form})


# -------------------------
# PROFIL UTILISATEUR
# -------------------------

@login_required
def profile_edit(request):
    """
    Modification du profil utilisateur (nom, email, téléphone, etc.)
    """
    user = request.user

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():

            try:
                with transaction.atomic():
                    user_form.save()
                    profile_form.save()

                messages.success(request, "Votre profil a été mis à jour.")
                return redirect("users:profile_edit")

            except Exception as e:
                logger.error(f"[Profile] Erreur mise à jour : {e}")
                messages.error(request, f"Une erreur interne est survenue : {e}")

        else:
            # Affiche toutes les erreurs des deux formulaires
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"[Profil] Erreur dans « {field} » : {error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"[Profil] Erreur dans « {field} » : {error}")

    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=user.profile)

    return render(request, "users/profile_edit.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })



@login_required
def address_list(request):
    """
    Liste des adresses de l'utilisateur (livraison + facturation).
    """
    addresses = request.user.addresses.all()

    return render(request, "users/address_list.html", {
        "addresses": addresses
    })


@login_required
def address_add(request):
    """
    Ajouter une nouvelle adresse.
    """
    if request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            messages.success(request, "Adresse ajoutée avec succès.")
            return redirect("users:address_list")

        else:
            # Affiche toutes les erreurs
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans « {field} » : {error}")

    else:
        form = AddressForm()

    return render(request, "users/address_add.html", {
        "form": form
    })


@login_required
def address_edit(request, pk):
    """
    Modifier une adresse existante.
    """
    address = get_object_or_404(Address, pk=pk, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)

        if form.is_valid():
            form.save()
            messages.success(request, "Adresse mise à jour.")
            return redirect("users:address_list")

        else:
            # Affiche toutes les erreurs
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans « {field} » : {error}")

    else:
        form = AddressForm(instance=address)

    return render(request, "users/address_edit.html", {
        "form": form,
        "address": address,
    })
