from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        max_length=10,
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Color_tag',
        unique=True
    )
    slug = models.SlugField(
        max_length=10,
        unique=True
    )

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        constraints = [
            models.UniqueConstraint(
                fields=['slug'],
                name='unique_slug'
            )
        ]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='name_ingradient'
    )
    measurement_unit = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='author_recipies',
        help_text='Автор рецепта',
    )
    name = models.CharField(
        max_length=300,
        verbose_name='title_resipies',
        help_text='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='image_recipies',
        help_text='Картинка рецепта',
    )
    text = models.TextField(
        verbose_name='text_recepies',
        help_text='Текст рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient, 
        through='IngredientsRecipe',
        related_name='recipes',
        verbose_name='list_ingredients',
        help_text='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag, 
        through='TagsRecipe',
        related_name='recipes',
        verbose_name='tag_recipies',
        help_text='Тэги рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='time_recipies',
        help_text='Время приготовления, мин',
        validators=[MinValueValidator(
            1, 'Укажите время приготовления, оно не может быть менее 1 минуты'
        )],
    )
    pub_date = models.DateTimeField(
        verbose_name='date_recipies',
        auto_now_add=True, 
        db_index=True,
        help_text='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(
            1, 'Укажите количество ингридиента, не менее 1.'
        )],
        help_text='Количество ингредиента',
    )

    class Meta:
        verbose_name = 'Ingredient in recipe'
        verbose_name_plural = 'Ingredients in recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe'
            )
        ]


class TagsRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='favorite_recipes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Shopping cart'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_cart'
            )
        ]
