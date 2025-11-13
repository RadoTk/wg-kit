from django.core.management.base import BaseCommand
from django.db import connection
from orders.models import Order

class Command(BaseCommand):
    help = "Supprime toutes les commandes et réinitialise l'ID auto-incrémenté"

    def handle(self, *args, **kwargs):
        # Suppression des commandes
        deleted = Order.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"{deleted[0]} objets supprimés (commandes + produits)"))

        # Réinitialisation de l'ID selon la base de données
        db_engine = connection.settings_dict['ENGINE']

        table_name = 'orders_order'  

        try:
            with connection.cursor() as cursor:
                if 'sqlite' in db_engine:
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
                    self.stdout.write(self.style.SUCCESS("ID réinitialisé (SQLite)"))
                elif 'postgresql' in db_engine:
                    cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;")
                    self.stdout.write(self.style.SUCCESS("ID réinitialisé (PostgreSQL)"))
                elif 'mysql' in db_engine:
                    cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")
                    self.stdout.write(self.style.SUCCESS("ID réinitialisé (MySQL)"))
                else:
                    self.stdout.write(self.style.WARNING("Base de données non prise en charge pour réinitialiser l'ID"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la réinitialisation de l'ID : {e}"))

        self.stdout.write(self.style.SUCCESS("✔️ Commande terminée."))
