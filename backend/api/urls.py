from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, UserViewSet,# SubscribeViewSet,
                       RecipeViewSet, TagViewSet)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
#router.register('users/subscriptions', SubscribeViewSet,basename='subscribes_list')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
