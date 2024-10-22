from django.core.management import BaseCommand
import csv

from products.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Read csv file
        reader = csv.reader(open('duplicated_products.csv'))

        ids = []
        for row in reader:
            ids.append(int(row[0]))

        Product.objects.filter(id__in=ids).delete()
