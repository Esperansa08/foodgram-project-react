from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet,  UserViewSet,
                       RecipeViewSet, TagViewSet)


router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
    # path('auth/', include('djoser.urls')),
    # path('auth/', include('djoser.urls.jwt')),
]
