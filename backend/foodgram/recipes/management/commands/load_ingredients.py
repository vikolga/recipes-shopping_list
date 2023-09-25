import csv
from typing import Any
from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.load_ingredient()

    def load_ingredient(self, file='ingredients.csv'):
        file_path = f'{settings.BASE_DIR}/data/{file}'
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                status, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )