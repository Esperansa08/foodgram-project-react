from django import forms
from django.shortcuts import get_object_or_404

from .models import IngredientInRecipe, Ingredient, Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('title', 'tags',
                  'cooking_time', 'description', 'image')
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'cooking_time': forms.NumberInput(attrs={'value': 1}),
        }

    cooking_time = forms.IntegerField(required=True, min_value=1)
    image = forms.ImageField(required=True)

    def save_recipe(self, recipe, ingredients):
        for title, amount in ingredients.items():
            ingredient = get_object_or_404(Ingredient, title=title)
            recipe_ingredients = IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount)
            recipe_ingredients.save()
