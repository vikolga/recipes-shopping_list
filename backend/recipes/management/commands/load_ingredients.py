import json
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.load_ingredient()

    def load_ingredient(self, *args, **kwargs):
        with open('data/ingredients.json',
                  newline='', encoding='utf-8') as f_ingredient:
            ingredients = json.loads(f_ingredient.read())
            for ingredient in ingredients:
                Ingredient.objects.get_or_create(**ingredient)
