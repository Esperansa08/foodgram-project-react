from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',)
    measurement_unit = models.TextField(
        max_length=200, verbose_name='единицы измерения')

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        verbose_name = 'Ингредиент'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='тег')
    color = ColorField(
        default='#FF0000',
        max_length=200,
        verbose_name="Цвет в HEX",
        unique=True,)

    class Meta:
        verbose_name_plural = 'Теги'
        verbose_name = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'], name='Каждому тэгу свой цвет!')]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.TextField(
        verbose_name='Название',
        max_length=200,
        help_text='Введите название')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='ингредиенты',
        help_text='Ингредиент из таблицы Ingredient',
        through='IngredientInRecipe')
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Автор из таблицы User')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(1)],)
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Теги из таблицы Tag',
        through='TagInRecipe')
    image = models.ImageField(
        verbose_name='Картинка, закодированная в Base64',
        blank=True,
        upload_to='images/')

    class Meta:
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name[:15]


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиенты',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепты',
        related_name='ingredient_list',
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Количество',
        help_text='Количество ингредиентов',)

    class Meta:
        verbose_name = 'Ингредиент-рецепт'
        verbose_name_plural = 'Ингредиент-рецепт'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Не должно быть одинаковых ингредиентов!')]

    def __str__(self):
        return (
            f"{self.ingredient.name} ({self.ingredient.measurement_unit})"
            f" - {self.amount} "
        )


class TagInRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег-рецепт'
        verbose_name_plural = 'Тег-рецепт'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='Не должно быть одинаковых тэгов!')]

    def __str__(self):
        return f'{self.tag_id} {self.recipe_id}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',)

    class Meta:
        verbose_name_plural = 'Избранное'
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_content')]

    def __str__(self):
        return f"{self.recipe}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь',)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт',)

    class Meta:
        verbose_name_plural = 'Список покупок'
        verbose_name = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='Не должно быть одинаковых рецептов!')]

    def __str__(self):
        return f"{self.user}"
