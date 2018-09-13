from django.db import models


class RecipeSource(models.Model):
    url = models.URLField(max_length=2100)
    name = models.CharField(max_length=250)
    
    
class Ingredient(models.Model):
    name = models.TextField()
    

class Category(models.Model):
    name = models.CharField(max_length=300)
    

class Recipe(models.Model):
    name = models.TextField()
    url = models.URLField(max_length=2100)
    
    
class RecipeCategory(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="categories", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="recipes", on_delete=models.CASCADE)
    
        
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, related_name="recipes", on_delete=models.CASCADE)
    