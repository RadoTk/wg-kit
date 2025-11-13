from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

# Formulaire pour gérer les informations utilisateur (nom, prénom, email)
class UserForm(forms.ModelForm):
    """
    Formulaire de gestion des informations de l'utilisateur.
    @why: Permet de gérer et valider les informations de base de l'utilisateur.
    @how: Les champs 'first_name', 'last_name' et 'email' sont définis ici pour l'utilisateur.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

# Formulaire pour gérer les informations du profil utilisateur (adresse, code postal, pays, téléphone)

class UserProfileForm(forms.ModelForm):
    """
    Formulaire de gestion des informations du profil utilisateur.
    @why: Permet de gérer et valider les informations supplémentaires du profil de l'utilisateur.
    @how: Les champs 'address', 'postal_code', 'country' et 'phone_number' sont définis ici pour le profil.
    """
    class Meta:
        model = UserProfile
        fields = ['address', 'postal_code', 'country', 'phone_number']

# Formulaire combiné qui gère à la fois l'utilisateur et son profil utilisateur

class CombinedUserProfileForm(forms.Form):
    """
    Formulaire combiné pour gérer simultanément les informations de l'utilisateur et de son profil.
    @why: Permet de gérer la création ou la modification de l'utilisateur et de son profil dans un seul formulaire.
    @how: Utilise deux formulaires internes (UserForm et UserProfileForm) pour valider et sauvegarder les données.
    """
    user_form: UserForm
    profile_form: UserProfileForm

    def __init__(self, *args, **kwargs):
        """
        Initialise le formulaire combiné avec les données d'utilisateur.
        @why: Préparer les formulaires pour l'utilisateur et son profil.
        @how: On passe l'instance de l'utilisateur et des données facultatives pour pré-remplir les formulaires.
        """
        user = kwargs.pop('user') # Récupère l'utilisateur à partir des arguments
        super().__init__(*args, **kwargs)
        
        try:
            # Initialisation du formulaire de l'utilisateur avec les données de l'utilisateur
            self.user_form = UserForm(instance=user, prefix='user', data=kwargs.get('data'))
        except Exception as e:
            # Gestion des erreurs liées à l'initialisation du formulaire
            print(f"Erreur lors de l'initialisation du formulaire utilisateur : {e}")
            self.user_form = UserForm(prefix='user')
        
        try:
            # Initialisation du formulaire du profil utilisateur avec les données du profil
            self.profile_form = UserProfileForm(instance=user.profile, prefix='profile', data=kwargs.get('data'))
        except Exception as e:
            # Gestion des erreurs liées à l'initialisation du formulaire de profil
            print(f"Erreur lors de l'initialisation du formulaire de profil utilisateur : {e}")
            self.profile_form = UserProfileForm(prefix='profile')


    def is_valid(self):
        """
        Vérifie si les deux formulaires sont valides.
        @why: S'assurer que les deux formulaires (utilisateur et profil) sont valides avant la sauvegarde.
        @how: Retourne True uniquement si les deux formulaires sont valides.
        """
        user_valid = self.user_form.is_valid()
        profile_valid = self.profile_form.is_valid()
        
        if not user_valid:
            print("Erreur : Le formulaire utilisateur n'est pas valide.")
        if not profile_valid:
            print("Erreur : Le formulaire de profil utilisateur n'est pas valide.")
        
        return user_valid and profile_valid
    

    def save(self):
        """
        Sauvegarde les données des deux formulaires.
        @why: Permet de sauvegarder les données de l'utilisateur et du profil utilisateur dans la base de données.
        @how: Sauvegarde d'abord les informations de l'utilisateur, puis celles du profil utilisateur.
        """
        try:
            self.user_form.save()  # Sauvegarde les informations de l'utilisateur
        except Exception as e:
            # Gestion des erreurs lors de la sauvegarde des informations utilisateur
            print(f"Erreur lors de la sauvegarde des informations utilisateur : {e}")
        
        try:
            self.profile_form.save()  # Sauvegarde les informations du profil
        except Exception as e:
            # Gestion des erreurs lors de la sauvegarde des informations du profil
            print(f"Erreur lors de la sauvegarde des informations du profil utilisateur : {e}")