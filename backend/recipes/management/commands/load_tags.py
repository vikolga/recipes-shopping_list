import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.load_tags()

    def load_tags(self, *args, **kwargs):
        with open('data/tags.json',
                  newline='', encoding='utf-8') as f_tags:
            tags = json.loads(f_tags.read())
            for tag in tags:
                Tag.objects.get_or_create(**tag)