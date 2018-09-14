from django.views.generic.base import TemplateView
from recipes.models import Category, Ingredient, Recipe
from rest_framework.views import APIView
from django.db.models.aggregates import Count
from rest_framework.response import Response
from django.db.models.expressions import Case, When
from django.db.models import F


class RecipeView(TemplateView):
    template_name = "recipes.html"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        categories = [{"id": category.id,
                       "name": category.name} for category in Category.objects.order_by("name")]
        ctx.update({"categories": categories})
        ingredients = [{"value": ingredient.id, "text": ingredient.name} for ingredient in Ingredient.objects.all()]
        ctx.update({"ingredients": ingredients})
        return ctx    

class FindRecipeView(TemplateView):
    template_name = "recipes_results.html"
    
    def get_recipe_json(self, recipe):
        categories = recipe.categories.values_list('category__name', flat=True)
        
        return {"title": recipe.name,
                "url": recipe.url,
                "categories": "" if not categories else ', '.join(categories)}
        
        
    def get_context_data(self, **kwargs):
        ctx = TemplateView.get_context_data(self, **kwargs)
        
        ingredients = [int(x) for x in self.request.GET.get('ingredients', '').split(',')] if self.request.GET.get('ingredients', None) else None
        categories = self.request.GET.getlist('categories', [])
        recipes_basic_fiter =  Recipe.objects.annotate(total_ing_num=Count("ingredients__ingredient_id"),
                                                       searched_ing_num=Count(Case(
                                                                        When(ingredients__ingredient_id__in=ingredients, then=1)))).\
                                            filter(searched_ing_num__lte=len(ingredients), searched_ing_num__gt=0)
        all_ingredient_recipes = recipes_basic_fiter.filter(total_ing_num=F("searched_ing_num"))
        one_missing_recipes = recipes_basic_fiter.filter(total_ing_num=(F("searched_ing_num") + 1))
        two_missing_recipes = recipes_basic_fiter.filter(total_ing_num=(F("searched_ing_num") + 2))
        more_than_two_missing_recipes = recipes_basic_fiter.filter(total_ing_num__gt=(F("searched_ing_num") + 2))
        
        if categories:
            all_ingredient_recipes = all_ingredient_recipes.filter(categories__category_id__in=[int(x) for x in categories])
            one_missing_recipes = one_missing_recipes.filter(categories__category_id__in=[int(x) for x in categories])
            two_missing_recipes = two_missing_recipes.filter(categories__category_id__in=[int(x) for x in categories])
            more_than_two_missing_recipes = more_than_two_missing_recipes.filter(categories__category_id__in=[int(x) for x in categories])
            
        ctx.update({"all_ingredients": [self.get_recipe_json(x) for x in all_ingredient_recipes],
                    "one_missing": [self.get_recipe_json(x) for x in one_missing_recipes],
                    "two_missing": [self.get_recipe_json(x) for x in two_missing_recipes],
                    "more_than_two_missing": [self.get_recipe_json(x) for x in more_than_two_missing_recipes],})
    
    
        return ctx
    
    
    
    
    