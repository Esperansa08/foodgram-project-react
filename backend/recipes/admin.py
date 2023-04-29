from django.contrib import admin
from django.utils.safestring import mark_safe

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    IngredientInRecipe,
    Favorite,
    Shoppinglist,
    TagInRecipe,
)


class IngredientsInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'text', 'cooking_time', 'preview')
    readonly_fields = ['preview']
    search_fields = ('name',)
    list_filter = (
        'author',
        'name',
        'tags',
    )
    exclude = ['ingredients', 'tags']

    def preview(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' width='60' />")


@admin.register(Ingredient)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe_id', 'recipe', 'amount')
    ordering = ('-recipe_id',)
    search_fields = ('ingredient',)
    list_filter = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    search_fields = ('user', 'recipe',)


@admin.register(Shoppinglist)
class Shopping_list_Admin(admin.ModelAdmin):
    list_display = ('recipe', 'user',)
    search_fields = ('recipe',)


@admin.register(TagInRecipe)
class TagInRecipeAdmin(admin.ModelAdmin):
    list_display = ('tag_id', 'tag', 'recipe_id', 'recipe')
    ordering = ('-recipe_id',)
    search_fields = (
        'tag',
        'recipe',
    )
    list_filter = (
        'recipe',
        'tag',
    )
