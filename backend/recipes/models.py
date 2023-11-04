from django.db import models
from django.core.validators import (MinValueValidator, MinLengthValidator,
                                    RegexValidator, MaxValueValidator)

from users.models import CustomUser


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код выбранного цвета.'
            )
        ]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name_plural = 'Теги'
        verbose_name = 'Тег'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'],
                name='unique_tagcolor'
            ),
        ]

    def __str__(self) -> str:
        return self.slug


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=200,
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        verbose_name = 'Ингредиент'
        ordering = ['name', ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_nameunit'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class TagRecipes(models.Model):
    """Промежуточная модель тегов в рецептах."""
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipetag'
            ),
        ]


class Recipe(models.Model):
    """Модель рецептов."""
    tags = models.ManyToManyField(
        Tag,
        through=TagRecipes,
        related_name='recipes',
        validators=[
            MinLengthValidator(
                1,
                message='Должен быть хотя бы один тег.'
            ),
        ]
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipes',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        validators=[
            MinLengthValidator(
                1,
                message='Должен быть хотя бы один ингредиент'
            ),
        ]
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
            MinValueValidator(
                1,
                message='Время приготовления не может быть менее 1 минуты.'),
            MaxValueValidator(
                900,
                message='Время приготовления не может быть больше 15 часов.'
            )
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепт'
        ordering = ['-pub_date', ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipeauthor'
            ),
        ]

    def __str__(self):
        return self.name


class IngredientRecipes(models.Model):
    """Промежуточная модель ингредиентов в рецептах."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_used'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_used'
    )
    amount = models.IntegerField(
        # validators=[
        #     MinValueValidator(1,
        #                       message='Минимальное количество ингредиентов 1.')
        # ],
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты в рецептах'
        verbose_name = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient.name} {self.ingredient.measurement_unit}'


class Favourite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favouriting'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favouriting'
    )

    class Meta:
        verbose_name_plural = 'Избранное'
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_userrecipes'
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в избранном {self.user}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name_plural = 'Списки покупок'
        verbose_name = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_usershopping'
            ),
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'
