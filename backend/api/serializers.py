import datetime as dt
from django.contrib.auth import get_user_model
from django.core import validators
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

#from reviews.models import Category, Comment, Genre, Review, Title
#from .exceptions import BadRating, IncorrectTitleInYear
from recipes.models import Recipe, Ingredient, Tag

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
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


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
    name = serializers.CharField(max_length=256)
    #amount = serializers.CharField()
       # validators=[])

#     def validate_score(self, value):
#         if not (value in range(1, 11)):
#             raise BadRating('Оценка должна быть в пределах от 1 до 10')
#         return value

    class Meta:
        model = Ingredient
        fields = ('id','name', 'amount', 'measurement_unit') 
        #lookup_field = 'name'


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
#     category = CategorySerializer(read_only=True)
#     genre = GenreSerializer(many=True, required=False)
#     rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
       # lookup_field = 'slug'

# class TitleSerializerWrite(serializers.ModelSerializer):
#     category = serializers.SlugRelatedField(slug_field='slug',
#                                             queryset=Category.objects.all())
#     genre = serializers.SlugRelatedField(many=True,
#                                          slug_field='slug',
#                                          queryset=Genre.objects.all())

#     rating = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = Title
#         fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
#                   'category')

#     def validate_year(self, value):
#         year_now = dt.date.today().year
#         print(year_now)
#         if value > year_now:
#             raise IncorrectTitleInYear('Передано некорректное значение года')
#         return value


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
