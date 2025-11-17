"""
Django management command: seed_users

Objectif
- Initialiser de façon déterministe et idempotente des rôles et des utilisateurs.
- Utiliser le modèle User (standard ou personnalisé via get_user_model()).
- Si un modèle Role existe (nom de modèle « Role »), l'utiliser; sinon faire un fallback vers Group.

Garanties fonctionnelles
- Exécutable via: `python manage.py seed_users`
- Vérifie les modèles (User, Role/Group)
- Idempotente: aucune duplication lors des ré-exécutions
- Hash des mots de passe via `set_password`
- Messages de confirmation + journalisation structurée
- Permissions déterministes par rôle/groupe

Garanties non-fonctionnelles
- Déterminisme total (mêmes entrées → même sortie)
- Fonctions courtes, une seule responsabilité, noms explicites

Rôles
- super-admin: accès total
- admin: permissions `view_*`
- user: aucune permission explicite

Utilisateurs (2 par rôle)
- super-admin1 : superadmin1@example.com / motdepasse1
- super-admin2 : superadmin2@example.com / motdepasse2
- admin1       : admin1@example.com       / motdepasse1
- admin2       : admin2@example.com       / motdepasse2
- user1        : user1@example.com        / motdepasse1
- user2        : user2@example.com        / motdepasse2
"""

from typing import Tuple, Type, Optional
import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

logger = logging.getLogger(__name__)


ROLE_DEFINITIONS = (
    {"name": "super-admin", "description": "Accès complet à toutes les fonctionnalités"},
    {"name": "admin", "description": "Accès administratif limité"},
    {"name": "user", "description": "Accès basique"},
)

USER_DEFINITIONS = (
    {"username": "super-admin1", "email": "superadmin1@example.com", "password": "motdepasse1", "role": "super-admin", "is_staff": True, "is_superuser": True},
    {"username": "super-admin2", "email": "superadmin2@example.com", "password": "motdepasse2", "role": "super-admin", "is_staff": True, "is_superuser": True},
    {"username": "admin1", "email": "admin1@example.com", "password": "motdepasse1", "role": "admin", "is_staff": True, "is_superuser": False},
    {"username": "admin2", "email": "admin2@example.com", "password": "motdepasse2", "role": "admin", "is_staff": True, "is_superuser": False},
    {"username": "user1", "email": "user1@example.com", "password": "motdepasse1", "role": "user", "is_staff": False, "is_superuser": False},
    {"username": "user2", "email": "user2@example.com", "password": "motdepasse2", "role": "user", "is_staff": False, "is_superuser": False},
)


def getRoleModelOrGroup() -> Tuple[Type, bool]:
    """Résout le modèle de rôle: retourne (RoleModel, isGroupFallback)."""
    for model in apps.get_models():
        if getattr(model._meta, "model_name", "") == "role":
            return model, False
    return Group, True


def setGroupPermissions(group: Group) -> None:
    """Assigne des permissions déterministes au groupe fourni."""
    if not isinstance(group, Group):
        return
    groupName = group.name
    if groupName == "super-admin":
        group.permissions.set(Permission.objects.all())
    elif groupName == "admin":
        group.permissions.set(Permission.objects.filter(codename__startswith="view_"))
    elif groupName == "user":
        group.permissions.clear()
    group.save()


class Command(BaseCommand):
    help = (
        "Initialise la base de données avec des rôles (Role/Group) et des utilisateurs prédéfinis. "
        "La commande est idempotente et peut être exécutée plusieurs fois sans créer de doublons."
    )

    def getUserModel(self):
        """Retourne le modèle User, ou lève CommandError en cas d'échec."""
        try:
            return get_user_model()
        except Exception as e:
            raise CommandError(f"Impossible d'obtenir le modèle User: {e}")

    def ensureRoles(self) -> Type:
        """Crée les rôles s'ils n'existent pas et assigne les permissions (si Group)."""
        roleModel, isGroupFallback = getRoleModelOrGroup()
        modelLabel = roleModel.__name__
        self.stdout.write(self.style.NOTICE(f"Vérification du modèle de rôle: {modelLabel}"))
        logger.info("Role model resolved to %s (group_fallback=%s)", modelLabel, isGroupFallback)

        for role in ROLE_DEFINITIONS:
            roleName = role["name"]
            if roleModel is Group:
                roleObj, created = Group.objects.get_or_create(name=roleName)
                setGroupPermissions(roleObj)
            else:
                roleObj, created = roleModel.objects.get_or_create(name=roleName)

            msg = f"Rôle {'créé' if created else 'existant'}: {roleName}"
            self.stdout.write(self.style.SUCCESS(msg) if created else self.style.NOTICE(msg))
            logger.info(msg)

        return roleModel

    def getExistingUser(self, userModel, username: str) -> Optional[object]:
        """Retourne l'utilisateur s'il existe, sinon None."""
        return userModel.objects.filter(username=username).first()

    def createUser(self, userModel, username: str, email: str, password: str, isStaff: bool, isSuperuser: bool) -> object:
        """Crée un utilisateur avec hash du mot de passe et flags explicites."""
        user = userModel.objects.create(username=username, email=email)
        user.is_staff = isStaff
        user.is_superuser = isSuperuser
        user.set_password(password)
        user.save()
        return user

    def assignRoleToUser(self, roleModel: Type, roleName: str, user: object) -> None:
        """Assigne le rôle/groupe à l'utilisateur de façon déterministe."""
        if roleModel is Group:
            group = Group.objects.get(name=roleName)
            group.user_set.add(user)
            return

        roleObj = roleModel.objects.get(name=roleName)
        if hasattr(roleObj, "users"):
            roleObj.users.add(user)

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Démarrage de la commande seed_users"))
        logger.info("Démarrage de seed_users")

        userModel = self.getUserModel()
        self.stdout.write(self.style.SUCCESS("Modèle User détecté"))
        logger.info("User model detected: %s", userModel.__name__)

        roleModel = self.ensureRoles()

        for u in USER_DEFINITIONS:
            username = u["username"]
            email = u["email"]
            password = u["password"]
            roleName = u["role"]
            isStaff = u["is_staff"]
            isSuperuser = u["is_superuser"]

            try:
                existingUser = self.getExistingUser(userModel, username)
                if existingUser is None:
                    newUser = self.createUser(userModel, username, email, password, isStaff, isSuperuser)
                    msg = f"Utilisateur créé: {username} ({email})"
                    self.stdout.write(self.style.SUCCESS(msg))
                    logger.info(msg)
                    self.assignRoleToUser(roleModel, roleName, newUser)
                else:
                    msg = f"Utilisateur existant: {username} ({email}) — aucun changement"
                    self.stdout.write(self.style.NOTICE(msg))
                    logger.info(msg)
                    self.assignRoleToUser(roleModel, roleName, existingUser)
            except Exception as e:
                logger.exception("Erreur lors de la création/assignation de l'utilisateur %s: %s", username, e)
                raise CommandError(f"Erreur lors de la création/assignation de l'utilisateur {username}: {e}")

        self.stdout.write(self.style.SUCCESS("Seed des rôles et utilisateurs terminé avec succès."))
        logger.info("Seed completed successfully")