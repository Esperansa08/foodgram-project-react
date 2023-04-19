from django.contrib import admin

from recipes.models import Recipe, Ingredient, Tag


# class GenreInline(admin.TabularInline):
#     model = GenreTitle
#     extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'text',
        'cooking_time')
    # search_fields = ('name',)
    # list_filter = ('year',)
    # empty_value_display = '-пусто-'
    #exclude = ['ingredients']


@admin.register(Ingredient)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('amount', 'name', 'measurement_unit')
    #ordering = ('-title_id',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug')
#     search_fields = ('name',)


# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('text', 'review_id', 'pub_date', 'author_id')
#     search_fields = ('text',)


# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ('title_id', 'author_id', 'text', 'score', 'pub_date')
