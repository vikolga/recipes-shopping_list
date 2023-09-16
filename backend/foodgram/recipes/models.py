from django.db import models
from django.core.validators import MinValueValidator
from users.models import CustomUser

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
    

class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        CustomUser,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipes'
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/image/',
        null=True,
        default=None
    )
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message ='Время приготовления не может быть менее 1 минуты.')
        ]
    )


class IngredientRecipes(models.Model):
    recipes = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Количество ингридиента не может быть менее единицы.')
        ]
    )

    def __str__(self) -> str:
        return f'{self.recipe} {self.ingredient}'