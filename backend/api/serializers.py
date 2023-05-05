from django.contrib.auth import get_user_model
from django.core import validators
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Subscribe
from .utils import clean_unique

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

        model = User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200)
    slug = serializers.CharField(
        max_length=50,
        validators=[
            validators.validate_slug,
            UniqueValidator(queryset=Tag.objects.all()),
        ],
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        lookup_field = 'slug'


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializerRead(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time',)

    def get_ingredients(self, obj):
        """Получение списка ингредиентов."""
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount'))
        return ingredients

    def get_is_in_shopping_cart(self, obj):
        """Находится ли в списке покупок."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_list.filter(recipe=obj).exists()

    def get_is_favorited(self, obj):
        """Находится ли в избранном."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()


class RecipeSerializerWrite(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(many=True, required=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True,
                                  required=True, validators=[clean_unique])

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time',)

    def validate_ingredients(self, ingredients):
        """Валидатор ингредиентов"""
        ingredient_list = []
        massage = 'Не должно быть повторяющихся ингредиентов'
        for ingredient in ingredients:
            print(ingredient)
            if int(ingredient['amount']) <= 0:
                raise ValidationError('Выберите кол-во для ингредиента')
            if ingredient['id'] in ingredient_list:
                raise ValidationError([{"ingredient": [massage]}, {}])
            ingredient_list.append(ingredient['id'])
        return ingredients

    def to_representation(self, instance):
        return RecipeSerializerRead(instance,
                                    context=self.context).data

    def create_ingredients(self, recipe, ingredients):
        """Создание списка ингредиентов"""
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients])

    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        return instance


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', )
        read_only_fields = ('email', 'username')

    def get_recipes(self, obj):
        """Получение рецептов."""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Подсчет рецептов у автора."""
        return Recipe.objects.filter(author=obj).count()

    def validate(self, data):
        """Проверка на подписки."""
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
