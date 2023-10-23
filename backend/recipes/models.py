from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator, RegexValidator, MaxValueValidator
from users.models import CustomUser


class Tag(models.Model):
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
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'],
                name='unique_tagcolor'
            ),
        ]

    def __str__(self) -> str:
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=200,
    )

    class Meta:
        ordering = ['name',]
        # уточнить поиск по частичному вхождению в начале названия ингредиента
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_nameunit'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class TagRecipes(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
    )


class Recipe(models.Model):
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
        ordering = ['-pub_date',]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipeauthor'
            ),
        ]

    def __str__(self):
        return self.name


class IngredientRecipes(models.Model):
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
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Количество ингредиента не может быть менее единицы.'
            ),
            MaxValueValidator(
                90000,
                message='Ингредиент не может быть больше 90000 единиц.'
            )
        ]
    )

    def __str__(self):
        return f'{self.ingredient.name} {self.ingredient.measurement_unit}'


class Favourite(models.Model):
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_userrecipes'
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в избранном {self.user}'


class ShoppingCart(models.Model):
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_usershopping'
            ),
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'
