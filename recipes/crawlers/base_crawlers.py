from requests_html import HTMLSession
import re 
import inflect
from recipes.models import Ingredient, Category, Recipe, RecipeCategory,\
    RecipeIngredient


class BaseCrawler(object):
    base_url = ""
    plural_eng = None
    MEASUEMENT_UNITS = ["cup", "c", "ounce", "fluid ounce", "oz", "fl oz", "teaspoon", "t", "tsp", "tablespoon", 
                    "tbl", "tbs", "tbsp", "gill", "ml", "g", "gram", "clove", "sprig", "lb", "kg", "kilogram", "cm", "centimeter",
                    "inch", "bunch", "sachet", "tin", "can", "litre", "jar", "sheet", "handfull", "splash", "dash", "scoop", "stick",
                    "handful", "few", "slice", "knob", "head", "pinch", "bulb", "wineglass", "generous", "tablespooons",
                    "block", "swig", "teaspooon", "drop", "rasher", "glass", "tesapoon", "stalk", "packet", "juice",
                    "bottle", "zest", "about", "drizzle"]
    DESCRIPTION_DICT = ["free range", "large", "heaped", "skinless", "boneless", "fresh", "low salt", "reduced sodium", "piece",
                    "of", "heaping", "level", "seasonal", "ripe", "mixed colour", "freshly", "quality",
                    "mixed", "colour", "color", "unsalted", "higher-welfare", "shelled", "an", "small", "medium", "tenderstem", "organic", "fine",
                    "thinly", "sliced", "other", "higher welfare", "thick", "thin", "long", "jarred", "good", "fat free", "good quality",
                    "corn fed", "big", "low fat", "thick cut", "chopped", "country style", "grated", "mixture   "]

    def __init__(self):
        self.plural_eng = inflect.engine()
        
    def crawl_site(self):
        raise NotImplementedError()

    def crawl_recipe(self, link):
        raise NotImplementedError()

    def request_link(self, link):
        try:
            session = HTMLSession()
            session.close()
            resp = session.get(link)
        except:
            resp = None
        finally:
            print("closing a session")
            session.close()
            del session
            
        return resp

    def is_ingredient_description(self, word):
        '''
            This utility receives a word and checks if this word is an amount of an ingredient
            or a description of an ingredient.
            We check if the word is a number or one characther, which means it shows the amount,
            or if the word appears in the measurment units dictionary.
            The utility takes care of plurals as well.
        '''
        word = word.lower().strip().strip(',').replace('-', ' ')

        # If the string is empty after the changes, it is not part of the ingredient
        if not word:
            return True

        is_amount = len(word) == 1 or re.search('.*\d+', word) is not None

        try:
            singular_word = self.plural_eng.singular_noun(word)
        except:
            return True

        is_measurment = word in  self.MEASUEMENT_UNITS or (singular_word and singular_word in  self.MEASUEMENT_UNITS)
        is_description = word in  self.DESCRIPTION_DICT or (singular_word and singular_word in  self.DESCRIPTION_DICT)

        return is_amount or is_measurment or is_description


    def handle_ingredient(self, ingredient):
        '''
        This utility receives an ingredient text from a recipe, and extracts the ingredient's name
        '''
        ing_txt = ingredient

        # If the entire text is uppercase, it means it is a name of a part of the recipe, 
        # and not an ingredient
        if ing_txt.isupper():
            ing_txt = None
        elif ing_txt:
            left_bracket_idx = ing_txt.find('(')
            right_bracket_idx = ing_txt.find(')')

            # Remove all text in brackets, because it's discriptive
            while (left_bracket_idx != -1 and right_bracket_idx != -1 and right_bracket_idx > left_bracket_idx):
                ing_txt = " ".join([ing_txt[:left_bracket_idx].strip(), ing_txt[right_bracket_idx + 1:].strip()])
                left_bracket_idx = ing_txt.find('(')
                right_bracket_idx = ing_txt.find(')')

            # In case we have two choices for ingredients, we take the second choice
            or_idx = ing_txt.find(" or ") 
            if  or_idx != -1:
                ing_txt = ing_txt[or_idx+4:]
            
            # Removing all quantitive, measurment, etc. words    
            first_part = ing_txt.split(' ', 1)[0]

            while ing_txt and  self.is_ingredient_description(first_part):
                txt_parts = ing_txt.split(' ', 1)

                # If the text contains only one word, we found the ingredient
                if len(txt_parts) == 1:
                    ing_txt = txt_parts[0]
                    break
                else:
                    # If the text contains more than one word, 
                    # we still need to check if some of the words are descriptive (amount, measurment, etc.)
                    ing_txt = txt_parts[1] 
                    first_part = ing_txt.split(' ', 1)[0]

            # Removing all text after a comman, because it's descriptive
            comma_idx = ing_txt.find(',')

            while comma_idx != -1:
                ing_txt = ing_txt[:comma_idx].strip()
                comma_idx = ing_txt.find(',')

        return ing_txt 

    def create_recipe(self, name, url, ingredients_name_list, categories_names_list):
        # Creating the recipe in the database. We don't create the recipe if a recipe with this link exists already in the DB
        recipe, created = Recipe.objects.get_or_create(url=url, defaults={"name": name})
        
        # Handling a new recipe
        if created:
            recipe_categories_list = []
        
            # Creating the new categories
            for category in categories_names_list:
                category, _ = Category.objects.get_or_create(name=category.lower().strip())
                recipe_categories_list.append(RecipeCategory(recipe=recipe, category=category))
            
            RecipeCategory.objects.bulk_create(recipe_categories_list)

            recipe_ingredients_list = []
            
            # Creting the new ingredients
            for ing_name in ingredients_name_list:
                singular_ing = self.plural_eng.singular_noun(ing_name.lower().strip())
                name = singular_ing or ing_name.lower().strip()
                ingredient, _ = Ingredient.objects.get_or_create(name=name)
                recipe_ingredients_list.append(RecipeIngredient(recipe=recipe, ingredient=ingredient))
                
            # Updating the ingredients and categories of the recipe
            RecipeIngredient.objects.bulk_create(recipe_ingredients_list)
