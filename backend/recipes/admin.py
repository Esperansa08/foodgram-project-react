from django.contrib import admin
from django.utils.safestring import mark_safe	

from recipes.models import (Recipe, Ingredient, Tag, IngredientInRecipe,
                         Favorites, Shopping_list)


class ingredientsInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'text',
        'cooking_time',
        'preview'
    )
    readonly_fields = ["preview"]
    search_fields = ('name',)
    list_filter = ('author','name', 'tags',)
    # empty_value_display = '-пусто-'
    exclude = ['ingredients','tags']

    def preview(self, obj):
        return mark_safe(f"<img src='{obj.image.url}' width='60' />")

@admin.register(Ingredient)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'measurement_unit')
    #ordering = ('-name',)
    list_filter = ('name',)
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe_id',
        'recipe',
        'amount')
    ordering = ('-recipe_id',)
    search_fields = ('ingredient',)
    list_filter = ('recipe',)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Shopping_list)
class Shopping_listAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount',)
    search_fields = ('name',)


# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ('title_id', 'author_id', 'text', 'score', 'pub_date')
