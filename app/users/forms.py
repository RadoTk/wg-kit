from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserForm(forms.ModelForm):
    """
    Formulaire de gestion des informations utilisateur.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserProfileForm(forms.ModelForm):
    """
    Formulaire de gestion du profil utilisateur.
    """
    class Meta:
        model = UserProfile
        fields = ['address', 'postal_code', 'country', 'phone_number']


class CombinedUserProfileForm(forms.Form):
    """
    Formulaire combiné utilisateur + profil.
    """
    user_form: UserForm
    profile_form: UserProfileForm

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.user_form = UserForm(
            data=kwargs.get('data'),
            instance=user,
            prefix="user"
        )
        self.profile_form = UserProfileForm(
            data=kwargs.get('data'),
            instance=user.profile,
            prefix="profile"
        )

    def is_valid(self):
        """Valide les deux sous-formulaires."""
        valid = self.user_form.is_valid() and self.profile_form.is_valid()

        if not valid:
            print("Formulaire combiné invalide")

        return valid

    def save(self):
        """Sauvegarde les données utilisateur + profil."""
        self.user_form.save()
        self.profile_form.save()
