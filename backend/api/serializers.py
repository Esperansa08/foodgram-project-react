import datetime as dt
from django.contrib.auth import get_user_model
from django.core import validators
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

#from reviews.models import Category, Comment, Genre, Review, Title
#from .exceptions import BadRating, IncorrectTitleInYear
from recipes.models import Recipe, Ingredient, Tag, IngredientInRecipe
from users.models import Subscribe
User = get_user_model()


class SignupSerializer(serializers.Serializer):
    username = serializers.RegexField(
        r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    email = serializers.EmailField(required=True, max_length=254)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не допустимо!'
            )
        return value


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name')
        #, 'is_subscribed')
        model = User

class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name')
        #, 'is_subscribed')
        model = Subscribe

class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = Recipe
        fields = ('username', 'confirmation_code')


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=200)
    #amount = serializers.CharField()
       # validators=[])

#     def validate_score(self, value):
#         if not (value in range(1, 11)):
#             raise BadRating('Оценка должна быть в пределах от 1 до 10')
#         return value

    class Meta:
        model = Ingredient
        fields = ('id','name', 'measurement_unit') 
        #lookup_field = 'name'


class TagSerializer(serializers.ModelSerializer):
#     category = CategorySerializer(read_only=True)
#     genre = GenreSerializer(many=True, required=False)
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
    is_favorited = serializers.BooleanField(read_only=True) #, required=False)
    is_in_shopping_cart= serializers.BooleanField(read_only=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'text','ingredients','cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

class RecipeSerializerRead(serializers.ModelSerializer):
    #ingredients = IngredientSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True) #, required=False)
    #rating = serializers.IntegerField(read_only=True)
    tags = TagSerializer(many=True)
    #ingredients = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
    
    def get_ingredients(self, obj):
        serializer = IngredientSerializer(obj.ingredients)
        return serializer.data     

class IngredientInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

        
class RecipeSerializerWrite(serializers.ModelSerializer):
    ingredients = serializers.SlugRelatedField(many=True, read_only=False,
                                         slug_field='id',
                                         queryset=Ingredient.objects.all())
    tags = serializers.SlugRelatedField(many=True, read_only=False,
                                         slug_field='id',
                                         queryset=Tag.objects.all())
    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name','text','cooking_time')


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
