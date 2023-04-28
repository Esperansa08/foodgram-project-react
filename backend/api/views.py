from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from djoser.views import UserViewSet
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    IngredientInRecipe,
    Favorite,
    Shopping_list,
)
from users.models import Subscribe

from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    RecipeSerializerRead,
    RecipeSerializerWrite,
    SubscribeSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    http_method_names = ["get", "post"]

    @action(detail=True, methods=["POST", "DELETE"],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request):
        """Подписываемся и отписываемся"""
        user = request.user
        author_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)
        if request.method == "POST":
            if user != author:
                Subscribe.objects.get_or_create(
                    user=request.user, author=author)
                serializer = UserSerializer(
                    user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            subscription = get_object_or_404(
                Subscribe, user=user, author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Получаем все подписки"""
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={
                "request": request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    search_fields = ("^name",)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    # serializer_class = RecipeSerializer
    # serializer_class = (RecipeSerializerRead, RecipeSerializerWrite)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializerRead
        return RecipeSerializerWrite

    def get_queryset(self):
        queryset = Recipe.objects.all()
        return queryset

    @action(detail=True, methods=["post", "delete"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.add(Favorite, request.user, pk)
        else:
            return self.delete(Favorite, request.user, pk)

    @action(detail=True, methods=["post", "delete"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.add(Shopping_list, request.user, pk)
        else:
            return self.delete(Shopping_list, request.user, pk)

    def add(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, model, user, pk):
        recipe_del = model.objects.filter(user=user, recipe__id=pk)
        if recipe_del.exists():
            recipe_del.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)
 
    @action(
        detail=False,
        permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_list__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        y = 750
        shopping_list = ('Список покупок : ')
        filename = f'{user.username}_shopping_list.pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        p = canvas.Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(TTFont('FreeSans',
                                       'static/FreeSans.ttf'))
        p.setFont('FreeSans', 16)
        p.drawString(100, y, 'Список покупок : ')
        for ingredient in ingredients:
            p.drawString(100, y, shopping_list)
            shopping_list = (f'* {ingredient["ingredient__name"]} '
                             f'({ingredient["ingredient__measurement_unit"]})'
                             f' - {ingredient["amount"]}')
            y -= 30
        p.showPage()
        p.save()

        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
