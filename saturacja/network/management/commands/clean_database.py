from django.core.management.base import BaseCommand
from network.models import Customer, Saturation

class Command(BaseCommand):
    help = 'Clean complete: Remove all Customer and Saturation records from the database'

    def handle(self, *args, **options):
        customer_count = Customer.objects.count()
        saturation_count = Saturation.objects.count()
        Customer.objects.all().delete()
        Saturation.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(
            f"Clean complete: Removed {customer_count} Customer records and {saturation_count} Saturation records."
        ))
