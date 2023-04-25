import datetime as dt
from django.contrib.auth import get_user_model
from django.core import validators
from django.db.models import F
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField

#from .exceptions import BadRating, IncorrectTitleInYear
from recipes.models import (Recipe, Ingredient, Tag, IngredientInRecipe,
                            Favorite, Shopping_list)
from users.models import Subscribe
User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')

        model = User

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author = obj).exists()
        #return user.subscribing.filter(user=user, author = obj).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id','name', 'measurement_unit') 


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200)
    slug = serializers.CharField(
        max_length=50,
        validators=[validators.validate_slug,
                    UniqueValidator(queryset=Tag.objects.all())])

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        lookup_field = 'slug'


class RecipeSerializer(serializers.ModelSerializer):
    #is_favorited = serializers.SerializerMethodField(read_only=True) #, required=False)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart= serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True) #, required=False)
    #rating = serializers.IntegerField(read_only=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def create(self, obj):
        pass
    
    def update(self, obj):
        pass

class IngredientInRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

class RecipeSerializerRead(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_in_shopping_cart= serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
    
    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount'))
        return ingredients
 
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Shopping_list.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        #return Favorite.objects.filter(recipe=obj, user=request.user).exists()
        return user.favorites.filter(recipe=obj).exists()
        
class RecipeSerializerWrite(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     read_only=True,
    #     #queryset=User.objects.all(),
    #     default=serializers.CurrentUserDefault(), )
    author = UserSerializer(read_only=True)
    #is_favorited = serializers.BooleanField(read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SlugRelatedField(many=True, read_only=False,
                                         slug_field='id',
                                         queryset=Ingredient.objects.all())
    tags = serializers.SlugRelatedField(many=True, read_only=False,
                                         slug_field='id',
                                         queryset=Tag.objects.all())
    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'author', 'image', 'name','text',
                  'cooking_time')


class SubscribeSerializer(UserSerializer):
    #email = serializers.ReadOnlyField(source='author.email')
    # id = serializers.ReadOnlyField(source='author.id')
    #username = serializers.ReadOnlyField(source='author.email')
    # first_name = serializers.ReadOnlyField(source='author.first_name')
    # last_name = serializers.ReadOnlyField(source='author.last_name')
    # is_subscribed = serializers.SerializerMethodField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = User

    # def get_recipes(self, obj):
    #     request = self.context['request']
    #     limit = request.GET.get('recipes_limit')
    #     queryset = obj.recipes.all()
    #     if limit:
    #         queryset = queryset[:int(limit)]
    #     return RecipeShortSerializer(queryset, many=True, read_only=True).data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author) #obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data
    
    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
    
    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )

    # def get_is_subscribed(self, obj):
    #     return Subscribe.objects.filter(
    #         user=obj.user, author=obj.author).exists()

# class ReviewSerializer(serializers.ModelSerializer):
#     author = serializers.SlugRelatedField(
#         slug_field='username',
#         queryset=User.objects.all(),
#         default=serializers.CurrentUserDefault(),
#     )

#     def validate_score(self, value):
#         if not (value in range(1, 11)):
#             raise BadRating('Оценка должна быть в пределах от 1 до 10')
#         return value

#     class Meta:
#         model = Review
#         fields = ('id', 'text', 'author', 'score', 'pub_date')


# class CommentSerializer(serializers.ModelSerializer):
#     author = serializers.StringRelatedField(many=False, read_only=True)

#     class Meta:
#         model = Comment
#         fields = ('id', 'text', 'author', 'pub_date',)
#         read_only_fields = ('id', 'author', 'pub_date',)
