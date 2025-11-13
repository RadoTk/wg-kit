from asyncio.log import logger
from django.db import models
from django.contrib.auth.models import User
from app.orders.models import Country 

from django.db.models.signals import post_save
from django.dispatch import receiver

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


class UserProfile(models.Model):
    """
    Modèle représentant le profil utilisateur.
    Ce modèle permet d'associer un profil personnalisé à chaque utilisateur, 
    avec des informations comme l'adresse, le code postal, le pays, et le numéro de téléphone.

    @why: Assurer qu'un utilisateur puisse avoir un profil distinct contenant des informations supplémentaires 
    au-delà de celles du modèle User.
    @how: Chaque utilisateur pourra avoir un profil qui est relié à lui via une relation OneToOne.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', help_text="L'utilisateur associé à ce profil")
    address = models.CharField(max_length=255, blank=True, help_text="Adresse de l'utilisateur") 
    postal_code = models.CharField(max_length=16, blank=True, help_text="Code postal de l'utilisateur")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True,  help_text="Pays de l'utilisateur")  
    phone_number = models.CharField(max_length=20, blank=True, help_text="Numéro de téléphone de l'utilisateur")  

    def __str__(self):
        """
        Retourne une représentation en chaîne de caractères du profil utilisateur.
        
        @why: Permet d'afficher le profil utilisateur de manière lisible.
        @how: Affiche "Profil de {username}" dans l'administration Django.
        """
        return f"Profil de {self.user.username}"


# Signal pour créer un profil utilisateur après la création d'un utilisateur
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée un profil utilisateur automatiquement à la création d'un utilisateur.
    
    @why: Assurer qu'un profil existe pour chaque utilisateur sans intervention manuelle.
    @how: Lors de la création d'un nouvel utilisateur, un profil correspondant est créé automatiquement.
    """
    if created:
        try:
            UserProfile.objects.create(user=instance)
        except Exception as e:
            # Gestion d'erreur en cas d'échec de la création du profil
            logger.error(f"Erreur lors de la création du profil pour l'utilisateur {instance.username}: {str(e)}")


# Signal pour sauvegarder le profil utilisateur à chaque sauvegarde de l'utilisateur
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Sauvegarde le profil utilisateur chaque fois que l'utilisateur est sauvegardé.
    
    @why: Assurer que les modifications du profil de l'utilisateur sont persistées en base de données.
    @how: Lors de la sauvegarde de l'utilisateur, le profil associé est également sauvegardé.
    """
    try:
        instance.profile.save()
    except Exception as e:
        # Gestion d'erreur si la sauvegarde du profil échoue
        logger.error(f"Erreur lors de la sauvegarde du profil pour l'utilisateur {instance.username}: {str(e)}")


class SignupForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé pour créer un utilisateur.
    
    @why: Permet de créer un utilisateur et de valider ses informations, tout en assurant que les champs essentiels comme le nom d'utilisateur, l'email, et les mots de passe sont bien renseignés.
    @how: Ce formulaire utilise les fonctionnalités de UserCreationForm de Django et les personnalise si nécessaire.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class SignupPage(Page):
    """
    Page d'inscription personnalisée qui affiche un formulaire pour permettre aux utilisateurs de s'inscrire sur le site.

    @why: Fournir un moyen aux utilisateurs de s'inscrire tout en étant intégré à l'architecture de Wagtail.
    @how: Lorsque le formulaire d'inscription est soumis, un utilisateur est créé et redirigé vers la page de connexion.
    """
    intro = models.TextField(help_text="Introductory text for the signup page")  # Texte d'introduction à afficher sur la page d'inscription

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def serve(self, request):
        """
        Gère le processus d'inscription de l'utilisateur. Si le formulaire est valide, l'utilisateur est créé et redirigé vers la page de connexion.

        @why: Permet de traiter l'inscription de l'utilisateur tout en validant les informations et en fournissant des retours.
        @how: Si le formulaire est valide, un utilisateur est créé, et une redirection vers la page de connexion est effectuée. En cas d'erreur, un message d'erreur est retourné.
        """
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save()  # Création de l'utilisateur
                    # Redirige après une inscription réussie
                    return redirect('users:login')  # Redirection vers la page de connexion
                except Exception as e:
                    # Gestion d'erreur si la création de l'utilisateur échoue
                    logger.error(f"Erreur lors de la création de l'utilisateur: {str(e)}")
                    form.add_error(None, "Une erreur s'est produite lors de l'inscription. Veuillez réessayer.")
        else:
            form = SignupForm()

        return render(request, 'users/signup_page.html', {'page': self, 'form': form})
