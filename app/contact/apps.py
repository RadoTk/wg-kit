from django.apps import AppConfig


class ContactConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # Full Python path to the app package to align with INSTALLED_APPS entry
    name = "app.contact"
    # Optional explicit label for consistency (database app label remains 'contact')
    label = "contact"
