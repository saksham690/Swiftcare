from django.core.management.base import BaseCommand
import requests
from SwiftCart.models import Medicine

class Command(BaseCommand):
    help = 'Syncs medicines from Flask API to Django Medicine model'

    def handle(self, *args, **kwargs):
        try:
            response = requests.get('http://127.0.0.1:5000/api/products')
            response.raise_for_status()
            products = response.json()
            for product in products:
                Medicine.objects.update_or_create(
                    name=product['name'],
                    defaults={
                        'description': product['description'],
                        'price': product['price'],
                        'image_url': product['image_url'],
                        'category': product['category'],
                        'stock_quantity': product['stock_quantity']
                    }
                )
            self.stdout.write(self.style.SUCCESS('Successfully synced medicines'))
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to sync medicines: {e}'))