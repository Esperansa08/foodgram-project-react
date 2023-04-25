from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg, OuterRef, Exists
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.views.generic import TemplateView
from djoser.views import UserViewSet

from recipes.models import (Ingredient, Recipe, Tag, IngredientInRecipe,
                         Favorite, Shopping_list)
from users.models import Subscribe
#from .filters import RecipeFilter
from .permissions import (IsAuthorOrReadOnly, IsAdminOrReadOnly)
from .serializers import (IngredientSerializer, RecipeSerializer, TagSerializer, 
                          RecipeSerializerRead, RecipeSerializerWrite,
                          SubscribeSerializer,
                          RecipeShortSerializer,
                         # TokenSerializer,
                           UserSerializer)

User = get_user_model()


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post']

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    
    def subscribe(self, request):
        """Подписываемся и отписываемся"""
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            if user != author:
                Subscribe.objects.get_or_create(user=request.user, author=author)
                serializer = UserSerializer(
                    user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                                user=user,
                                                author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=False,
        permission_classes=[IsAuthenticated])  
    def subscriptions(self, request):
        """Получаем все подписки"""
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)
    

   
class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    search_fields = ('^name',)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)



class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    #queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    #serializer_class = RecipeSerializer
    serializer_class = (RecipeSerializerRead, RecipeSerializerWrite)
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerRead
        return RecipeSerializerWrite
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        #queryset = self.annotate_qs_is_favorite_field(queryset)
        return queryset

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_fav(Favorite, request.user, pk)
        else:
            return self.delete_fav(Favorite, request.user, pk)
        
    def add_fav(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_fav(self, model, user, pk): 
        recipe_del = model.objects.filter(user=user, recipe__id=pk)
        if recipe_del.exists():
            recipe_del.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)   

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
#     permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
#     pagination_class = LimitOffsetPagination
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('name',)
#     lookup_field = 'slug'

def download_shopping_cart():
    pass




# class CategoryViewSet(mixins.ListModelMixin,
#                       mixins.CreateModelMixin, mixins.DestroyModelMixin,
#                       viewsets.GenericViewSet):
#     queryset = Category.objects.all()
#     permission_classes = (IsAdminOrReadOnly,)
#     serializer_class = CategorySerializer
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('name',)
#     lookup_field = 'slug'


# class ReviewCommentViewSet(viewsets.ModelViewSet):
#     def get_title(self):
#         title_id = self.kwargs.get("title_id")
#         if not Title.objects.filter(pk=title_id).exists():
#             raise TitleOrReviewNotFound(
#                 detail='Не найдено произведение или отзыв',
#                 code=status.HTTP_404_NOT_FOUND
#             )
#         return Title.objects.get(pk=title_id)


# class ReviewViewSet(ReviewCommentViewSet):
#     permission_classes = IsAuthorModeratorAdminOrReadOnly,
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer

#     def get_review(self):
#         review_id = self.kwargs.get("pk")
#         if not Review.objects.filter(pk=review_id).exists():
#             raise TitleOrReviewNotFound(
#                 detail='Не найдено произведение или отзыв',
#                 code=status.HTTP_404_NOT_FOUND
#             )
#         return Review.objects.get(pk=review_id)

#     def get_queryset(self):
#         return self.get_title().reviews.all()

#     def perform_create(self, serializer):
#         author = self.request.user
#         title = self.get_title()
#         if title.reviews.filter(author=author).exists():
#             raise IncorrectAuthorReview(
#                 'Этот автор уже оставлял отзыв к произведению')
#         serializer.save(
#             author=author,
#             title=title
#         )

#     def get_patch_author(self):
#         if self.request.method != 'PATCH':
#             return self.request.user
#         if not (self.request.user.is_moderator
#                 or self.request.user.is_admin):
#             return self.request.user
#         return self.get_review().author

#     def perform_update(self, serializer):
#         author = self.get_patch_author()
#         title = self.get_title()
#         serializer.save(
#             author=author,
#             title=title
#         )


# class CommentViewSet(ReviewCommentViewSet):
#     permission_classes = IsAuthorModeratorAdminOrReadOnly,
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer

#     def get_review(self):
#         review_id = self.kwargs.get("review_id")
#         if not Review.objects.filter(pk=review_id).exists():
#             raise TitleOrReviewNotFound(
#                 detail='Не найдено произведение или отзыв',
#                 code=status.HTTP_404_NOT_FOUND
#             )
#         return Review.objects.get(pk=review_id)

#     def get_queryset(self):
#         return self.get_review().comments.all()

#     def perform_create(self, serializer):
#         author = self.request.user
#         self.get_title()
#         review = self.get_review()
#         serializer.save(
#             author=author,
#             review=review
#         )

#     def perform_update(self, serializer):
#         author = self.request.user
#         self.get_title()
#         review = self.get_review()
#         serializer.save(
#             author=author,
#             review=review
#         )

