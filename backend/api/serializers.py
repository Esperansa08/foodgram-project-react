from django.contrib.auth import get_user_model
from django.core import validators
from django.db.models import F
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import PrimaryKeyRelatedField
from django.db import transaction


from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    IngredientInRecipe,
    Shopping_list,
    Favorite)
from users.models import Subscribe

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

        model = User


class UserSerializer(serializers.ModelSerializer):
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


# class RecipeSerializer(serializers.ModelSerializer):
#     #is_favorited = serializers.SerializerMethodField(read_only=True)
#  #, required=False)
#     is_favorited = serializers.BooleanField(read_only=True)
#     is_in_shopping_cart= serializers.SerializerMethodField(read_only=True)
#     image = Base64ImageField()
#     author = UserSerializer()
#     ingredients = IngredientSerializer(many=True) #, required=False)
#     #rating = serializers.IntegerField(read_only=True)
#     tags = TagSerializer(many=True)

#     class Meta:
#         model = Recipe
#         fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
#                   'is_in_shopping_cart', 'name', 'image', 'text',
#                   'cooking_time')

#     def create(self, obj):
#         pass

#     def update(self, obj):
#         pass


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializerRead(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
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
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount'))
        return ingredients

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Shopping_list.objects.filter(
            recipe=obj, user=request.user).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=user).exists()


def clean_unique(ingredients):
    """Валидатор, оставляющий только уникальные значения"""
    return list(set(ingredients))


class RecipeSerializerWrite(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(many=True, required=True,
                                               validators=[clean_unique])
    #ingredients = serializers.SerializerMethodField()
    # ingredients = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=False,
    #     slug_field="id",
    #     queryset=Ingredient.objects.all())
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True,
                                  required=True, validators=[clean_unique])
    id = serializers.ReadOnlyField()
    # tags = serializers.SlugRelatedField(
    #     many=True, read_only=False, slug_field="id", queryset=Tag.objects.all()
    # )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',)

    # def validate_ingredients(self, ingredients):
    #     if not ingredients.exist():
    #         raise ValidationError('Ингредиенты должны быть!')
    #     list_ingredients = []
    #     for ingredient in ingredients:
    #         if ingredient in list_ingredients:
    #             raise ValidationError('Ингредиенты не должны повторяться!')
    #         list_ingredients.append(ingredient)
    #         print(list_ingredients, ingredient)
    #     return ingredients
                
    def validate_ingredients(self, ingredients):
        """Валидатор ингредиентов"""
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                ValidationError('Выберите кол-во для ингредиента')
        return ingredients
    
    # @transaction.atomic
    # def tags_and_ingredients_set(self, recipe, tags, ingredients):
    #     recipe.tags.set(tags)
    #     IngredientInRecipe.objects.bulk_create(
    #         [IngredientInRecipe(
    #             recipe=recipe,
    #             ingredient=Ingredient.objects.get(id=ingredient['id']),
    #             amount=ingredient['amount']
    #         ) for ingredient in ingredients]
    #     )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )
        #self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe


    # def create(self, validated_data):
    #     ingredients = validated_data.pop('ingredients')
	# 	#directions = validated_data.pop('directions')
    #     #author_id = validated_data.user
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     recipe.tags.set(tags)
	# 	# Save the ingredients
    #     for ingredient in ingredients:
    #         ingredient = Ingredient.objects.get(id=ingredient.get('id'))
    #         recipe.ingredients.add(ingredient)
			
	# 	# Save the directions
	# 	# for direction in directions:
	# 	# 	Direction.objects.create(recipe=recipe, **direction)
			
    #     return recipe
#     def get_ingredients(self, obj):
#         ingredients = Ingredient.objects.filter(id=obj.id)
#           #  "id",
#         if obj.amount <= 0:
#             raise ValidationError('''Количество ингредиентов должно быть больше
# 0!''')
#         return ingredients
# class RecipeSerializerWrite(serializers.ModelSerializer):
#     # author = serializers.SlugRelatedField(
#     #     slug_field='username',
#     #     read_only=True,
#     #     #queryset=User.objects.all(),
#     #     default=serializers.CurrentUserDefault(), )
#     # author = UserSerializer(read_only=True)
#     # #is_favorited = serializers.BooleanField(read_only=True)
#     # image = Base64ImageField()
#     # ingredients = serializers.SlugRelatedField(many=True, read_only=False,
#     #                                      slug_field='id',
#     #                                      queryset=Ingredient.objects.all())
#     # tags = serializers.SlugRelatedField(many=True, read_only=False,
#     #                                      slug_field='id',
#     #                                      queryset=Tag.objects.all())
    
#     tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(),
#                                   many=True)
#     author = UserSerializer(read_only=True)
#     ingredients = IngredientInRecipeSerializer(many=True)
#     image = Base64ImageField()
#     class Meta:
#         model = Recipe
#         fields = ('ingredients', 'tags', 'author', 'image', 'name','text',
#                   'cooking_time')

#     @transaction.atomic
#     def create_ingredients_amounts(self, ingredients, recipe):
#         IngredientInRecipe.objects.bulk_create(
#             [IngredientInRecipe(
#                 ingredient=Ingredient.objects.get(id=ingredient['id']),
#                 recipe=recipe,
#                 amount=ingredient['amount']
#             ) for ingredient in ingredients]
#         )
   # @transaction.atomic
    # def create_ingredients(self, recipe, ingredients):
    #     IngredientInRecipe.objects.bulk_create(
    #         [IngredientInRecipe(
    #             recipe=recipe,
    #             ingredient_id=ingredient['id'], #Ingredient.objects.get(id=ingredient['id']),
    #             #ingredient_id=ingredient['id'],
    #            # ingredient_id=ingredient.get('id'),
    #             amount=ingredient['amount'],
    #         ) for ingredient in ingredients])
    #@atomic
    # def create_ingredients(self, recipe, ingredients):
    #     IngredientInRecipe.objects.bulk_create(
    #         [IngredientInRecipe(
    #             recipe=recipe,
    #             ingredient_id=row.get('id'),
    #             amount=row.get('amount'),
    #         ) for row in ingredients])
    # #@atomic
    # def create(self, validated_data):
    #     request = self.context.get('request')
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')
    #     recipe = Recipe.objects.create(author=request.user,
    #                                    **validated_data)
    #     self.create_ingredients(recipe, ingredients)
    #     recipe.tags.set(tags)
    #     return recipe
    # @transaction.atomic
    # def create(self, validated_data):
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')
    #     recipe = Recipe.objects.create(**validated_data)
    #     recipe.tags.set(tags)
    #     self.create_ingredients_amounts(recipe=recipe,
    #                                     ingredients=ingredients)
    #     return recipe

#     @transaction.atomic
#     def update(self, instance, validated_data):
#         tags = validated_data.pop('tags')
#         ingredients = validated_data.pop('ingredients')
#         instance = super().update(instance, validated_data)
#         instance.tags.clear()
#         instance.tags.set(tags)
#         instance.ingredients.clear()
#         self.create_ingredients_amounts(recipe=instance,
#                                         ingredients=ingredients)
#         instance.save()
#         return instance

#     def to_representation(self, instance):
#         request = self.context.get('request')
#         context = {'request': request}
#         return RecipeSerializerRead(instance,
#                                     context=context).data



class SubscribeSerializer(UserSerializer):
    # email = serializers.ReadOnlyField(source='author.email')
    # id = serializers.ReadOnlyField(source='author.id')
    # username = serializers.ReadOnlyField(source='author.email')
    # first_name = serializers.ReadOnlyField(source='author.first_name')
    # last_name = serializers.ReadOnlyField(source='author.last_name')
    # is_subscribed = serializers.SerializerMethodField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', )
        model = User

    # def get_recipes(self, obj):
    #     request = self.context['request']
    #     limit = request.GET.get('recipes_limit')
    #     queryset = obj.recipes.all()
    #     if limit:
    #         queryset = queryset[:int(limit)]
    # return RecipeShortSerializer(queryset, many=True, read_only=True).data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)  # obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
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

    # def get_is_subscribed(self, obj):
    #     return Subscribe.objects.filter(
    #         user=obj.user, author=obj.author).exists()

