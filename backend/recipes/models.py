from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from colorfield.fields import ColorField

User = get_user_model()

class Ingredient(models.Model):
    # amount = models.PositiveIntegerField(
    #     default=0,
    #     verbose_name='Количество',
    #     help_text='Количество ингредиентов')
    name = models.CharField(
        max_length=200,
        #unique=True,
        verbose_name='Название ингредиента')
    measurement_unit = models.TextField(
        max_length=200,
        verbose_name='единицы измерения')

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
        verbose_name='Цвет в HEX',
        unique=True,) 
        #CharField(
        # max_length=256,
        # default='#FF0000',
        # verbose_name='Цвет в HEX')
    
    class Meta:
        verbose_name_plural = 'Теги'
        verbose_name = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'],
                name='Каждому тэгу свой цвет!'
            )
        ]    

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.TextField(
        verbose_name='Название',
        max_length=200,
        help_text='Введите название')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredient',
        #on_delete=models.CASCADE,
        verbose_name='ингредиенты',
        help_text='Ингредиент из таблицы Ingredient',
        through='IngredientInRecipe')
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта',
        help_text='Автор из таблицы User')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators = [MinValueValidator(1)],)
    tags = models.ManyToManyField(
        Tag,
        related_name='tag',
        #on_delete=models.CASCADE,
        verbose_name='Теги',
        help_text='Теги из таблицы Tag',
        through='TagInRecipe')
    is_favorited = models.BooleanField(
        # null=True,
        # blank=True,
        default=False,
        verbose_name='Находится ли в избранном')
    is_in_shopping_cart= models.BooleanField(
        # null=True,
        # blank=True,
        default=False,
        verbose_name='Находится ли в корзине') 
    image = models.ImageField(
        verbose_name='Картинка, закодированная в Base64',
        blank=True,
        upload_to='images/')
        # height_field=None,
        # width_field=None,
        # max_length=100)
        #,null=True
        #**options)
    
    class Meta:
        verbose_name_plural = 'Рецепты'
        verbose_name = 'Рецепты'

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
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        default=0,
        validators = [MinValueValidator(0)],
        verbose_name='Количество',
        help_text='Количество ингредиентов')
    
    class Meta:
        verbose_name = 'Ингредиент-рецепт'
        verbose_name_plural = 'Ингредиент-рецепт'

    def __str__(self):
        return f'{self.ingredient_id} {self.recipe_id}'
    

class TagInRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэг-рецепт'
        verbose_name_plural = 'Тэг-рецепт'

    def __str__(self):
        return f'{self.tag_id} {self.recipe_id}'
    
class Favorites(models.Model):
    name = models.ForeignKey(
        Recipe,
        related_name='favorite',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта')
    # author = models.ForeignKey(
    #     Recipe,
    #     null=False,
    #     default=0,
    #     on_delete=models.CASCADE,
    #     verbose_name='Автор рецепта',)

    # image = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # cooking_time = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Избранное'
        verbose_name = 'Избранное'
        # constraints = [models.UniqueConstraint(
        #         fields=['name', 'author'],
        #         name='Возможен только один отзыв на произведение')]

    def __str__(self):
        return f'{self.name}'
    
    
class Shopping_list(models.Model):
    name = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # image = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # cooking_time = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(IngredientInRecipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        default=0,
        validators = [MinValueValidator(0)],
        verbose_name='Количество',
        help_text='Количество ингредиентов')
    class Meta:
        verbose_name_plural = 'Список покупок'
        verbose_name = 'Списки покупок'

    def __str__(self):
        return f'{self.name_id}'

    def augment_amount(self, amount):
        self.amount = self.amount + int(amount)
        self.save()