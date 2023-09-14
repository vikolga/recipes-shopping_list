from django.db import models

# Create your models here.
class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'],
                name='unique_tagcolor'
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=200,
    )
    
    class Meta:
        ordering = ['name',] #уточнить поиск по частичному вхождению в начале названия ингредиента
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_nameunit'
            ),
        ]
    
    def __str__(self) -> str:
        return f'{self.name} - {self.measurement_unit}'