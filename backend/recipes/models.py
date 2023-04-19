from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class Ingredient(models.Model):
    amount = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество',
        help_text='Количество ингредиентов')
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Название ингредиента')
    measurement_unit = models.IntegerField(verbose_name='единицы измерения')

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        verbose_name = 'Ингредиент'

    def __str__(self):
        return self.name

class Recipe(models.Model):
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='ingredient',
        on_delete=models.CASCADE,
        verbose_name='ингредиенты',
        help_text='Ингредиент из таблицы Ingredient')
    is_favorited = models.BooleanField(verbose_name='Находится ли в избранном')
    is_in_shopping_cart= models.BooleanField(
        verbose_name='Находится ли в корзине') 
    text = models.TextField(
        'Описание',
        help_text='Введите описание')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта',
        help_text='Автор из таблицы User')
    image = models.ImageField(
        'Картинка',
        #upload_to='posts/',
        blank=True)
    
    class Meta:
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепты'

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название тега')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='тег')

    class Meta:
        verbose_name_plural = 'Теги'
        verbose_name = 'Теги'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Ингредиент-рецепт'
        verbose_name_plural = 'Ингредиент-рецепт'

    def __str__(self):
        return f'{self.ingredient_id} {self.recipe_id}'