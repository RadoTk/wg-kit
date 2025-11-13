from django.contrib.auth.decorators import login_required  # Décorateur pour protéger les vues et nécessiter une connexion
from django.shortcuts import render, redirect  # Fonctions pour afficher et rediriger les pages
from django.contrib import messages  # Permet d'afficher des messages flash à l'utilisateur
from .forms import UserForm, UserProfileForm  # Formulaires pour les données utilisateur et profil

from django.contrib.auth import logout  # Fonction pour déconnecter un utilisateur
from django.contrib.auth.views import LoginView  # Vue de connexion fournie par Django


# Vue de connexion personnalisée
class UserLoginView(LoginView):
    template_name = 'users/login.html'  # Spécifie le modèle de la page de connexion


# Vue pour modifier le profil de l'utilisateur (accessible uniquement aux utilisateurs connectés)
@login_required
def profile_edit(request):
    """
    Cette vue permet à un utilisateur connecté de modifier son profil.
    @why: Cela garantit que seuls les utilisateurs connectés peuvent modifier leurs informations personnelles.
    @how: L'utilisateur soumet un formulaire avec ses nouvelles informations, qui est ensuite validé et sauvegardé.
    """

    user = request.user  # Récupère l'utilisateur actuellement connecté
    profile = user.profile  # Récupère le profil de l'utilisateur, en supposant qu'il existe

    # Traitement du formulaire lorsque la méthode est POST
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)  # Formulaire de l'utilisateur
        profile_form = UserProfileForm(request.POST, instance=profile)  # Formulaire du profil utilisateur

        # Vérifie si les deux formulaires sont valides
        if user_form.is_valid() and profile_form.is_valid():
            try:
                user_form.save()  # Sauvegarde les données de l'utilisateur
                profile_form.save()  # Sauvegarde les données du profil

                # Message de succès affiché à l'utilisateur
                messages.success(request, "Votre profil a été mis à jour avec succès.")
                return redirect('users:profile_edit')  # Redirige vers la page de modification du profil

            except Exception as e:
                # Gestion des erreurs lors de la sauvegarde
                messages.error(request, f"Erreur lors de la mise à jour du profil: {str(e)}")
        else:
            # Affiche un message d'erreur si le formulaire est invalide
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        # Si la méthode n'est pas POST, on préremplit les formulaires avec les données existantes de l'utilisateur
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    # Contexte passé au template pour afficher les formulaires
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'users/profile_edit.html', context)  # Affiche la page de modification de profil


# Fonction pour déconnecter un utilisateur
def user_logout(request):
    """
    Permet à un utilisateur de se déconnecter.
    @why: Permet à l'utilisateur de mettre fin à sa session active.
    @how: La fonction logout de Django est appelée pour déconnecter l'utilisateur.
    """
    logout(request)  # Déconnecte l'utilisateur actuel
    messages.success(request, "Vous avez été déconnecté avec succès.")  # Message de succès
    return redirect('users:login')  # Redirige l'utilisateur vers la page de connexion


# Vue pour l'inscription d'un utilisateur
def signup(request):
    """
    Permet à un nouvel utilisateur de s'inscrire.
    @why: Les utilisateurs doivent créer un compte pour accéder à certaines fonctionnalités du site.
    @how: L'utilisateur soumet un formulaire avec son nom, son email, et ses informations de profil.
    """

    if request.method == 'POST':
        # Création des formulaires d'inscription
        user_form = UserForm(request.POST)  # Formulaire pour l'utilisateur
        profile_form = UserProfileForm(request.POST)  # Formulaire pour le profil utilisateur
        
        # Vérification que les formulaires sont valides
        if user_form.is_valid() and profile_form.is_valid():
            try:
                user = user_form.save()  # Crée et sauvegarde l'utilisateur
                profile = profile_form.save(commit=False)  # Crée le profil, mais ne le sauve pas encore

                profile.user = user  # Lie le profil à l'utilisateur
                profile.save()  # Sauvegarde le profil

                # Message de succès
                messages.success(request, "Votre compte a été créé avec succès !")
                return redirect('users:login')  # Redirige vers la page de connexion après l'inscription réussie

            except Exception as e:
                # Gestion des erreurs lors de l'enregistrement
                messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
        else:
            # Affiche un message d'erreur si les formulaires ne sont pas valides
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        # Si la méthode n'est pas POST, on affiche les formulaires vides
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Contexte passé au template pour afficher les formulaires d'inscription
    return render(request, 'users/signup.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
