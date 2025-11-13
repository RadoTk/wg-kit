from django.core.management.base import BaseCommand
from app.orders.models import OrderStatus

class Command(BaseCommand):
    help = 'Crée les statuts de commande par défaut'

    def handle(self, *args, **options):
        status_data = [
            ('new', 'Nouvelle', '#007bff', 0),
            ('in_progress', 'En cours', '#ffc107', 1),
            ('packaged', 'Emballée', '#17a2b8', 2),
            ('in_delivery', 'En livraison', '#fd7e14', 3),
            ('delivered', 'Livrée', '#28a745', 4),
            ('cancelled', 'Annulée', '#dc3545', 5),
        ]
        
        created_count = 0
        for code, name, color, sort_order in status_data:
            status, created = OrderStatus.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'color': color,
                    'is_active': True,
                    'sort_order': sort_order
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Statut créé: {name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'{created_count} statuts créés avec succès')
        )