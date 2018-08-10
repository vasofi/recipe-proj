from requests_html import HTMLSession
import inflect
import re
import time 
measurment_units = ["cup", "c", "ounce", "fluid ounce", "oz", "fl oz", "teaspoon", "t", "tsp", "tablespoon", 
                    "tbl", "tbs", "tbsp", "gill", "ml", "g", "gram", "clove", "sprig", "lb", "kg", "kilogram", "cm", "centimeter",
                    "inch", "bunch", "sachet", "tin", "can", "litre", "jar", "sheet", "handfull", "splash", "dash", "scoop"]
description_dict = ["free range", "large", "heaped", "skinless", "boneless", "fresh", "low salt", "reduced sodium", "piece",
                    "of", "heaping", "level", "seasonal", "ripe", "mixed colour", "freshly", "quality",
                    "mixed", "colour", "color", "unsalted", "higher-welfare", "shelled", "an", "small", "medium", "tenderstem", "organic", "fine"]
base_url = "https://www.jamieoliver.com"
base_course_url = "https://www.jamieoliver.com/recipes/category/course/"

p = inflect.engine()
session = HTMLSession()

def is_ingredient_description(word):
    '''
        This utility receives a word and checks if this word is an amount of an ingredient
        or a description of an ingredient.
        We check if the word is a number or one characther, which means it shows the amount,
        or if the word appears in the measurment units dictionary.
        The utility takes care of plurals as well.
    '''
    word = word.strip().strip(',').replace('-', ' ')
    is_amount = len(word) == 1 or re.search('.*\d+', word) is not None
    singular_word = p.singular_noun(word)
    is_measurment = word in measurment_units or (singular_word and singular_word in measurment_units)
    is_description = word in description_dict or (singular_word and singular_word in description_dict)


    return is_amount or is_measurment or is_description

def handle_ingredient(ingredient):
    '''
    This utility receives an ingredient text from a recipe, and extracts the ingredient's name
    '''
    ing_txt = ingredient.text

    # If the entire text is uupercase, it means it is a name of a part of the recipe, 
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

        # Removing all quantitive, measurment, etc. words    
        first_part = ing_txt.split(' ', 1)[0]

        while ing_txt and is_ingredient_description(first_part):
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

        # In case we have two choices for ingredients, we take the second choice
        or_idx = ing_txt.find(" or ") 
        if  or_idx != -1:
            ing_txt = ing_txt[or_idx+4:]
           
    return ing_txt 

def crawl_recipe(link):
    '''
        This utillity receive a link to a recipe and prints the recipe's name,
        recipe's categories(Italian, dinner, etc.) and the recipe's ingredients
    '''
    recipe_resp = session.get(base_url + link)

    while recipe_resp.status_code == 403:
        time.sleep(1)
        recipe_resp = session.get(base_url + link)

    recipe_resp.html.render()
    blacklisted_categories = ["book", "jamie cooks italy", "jamie magazine"]
    recipe_tags = []
    
    for tag in recipe_resp.html.find('.tags-list > a'):
        category = tag.text

        if category:
            category = category.strip().strip(',')

            if category.lower() not in blacklisted_categories:
                recipe_tags.append(category)
    
    recipe_title = recipe_resp.html.find('h1', first=True).text
    
    # Checking if the page has duplicate ingredients list
    metric_ingred_list = recipe_resp.html.find('ul.ingred-list.metric')

    if metric_ingred_list:
        ingredients_html = recipe_resp.html.find('ul.ingred-list.metric > li')
    else:
        ingredients_html = recipe_resp.html.find('ul.ingred-list > li')
    ingredients_list = []

    for ingredient in ingredients_html:
        ing_name = handle_ingredient(ingredient)

        if ing_name:
            ingredients_list.append(ing_name)

    print('-----------------------------NEW RECIPE-----------------------------')
    print("Recipe name: ", recipe_title)
    print("Recipe categories: ", ', '.join(recipe_tags))
    print("Ingredients: ", ingredients_list)

def crawl_category_page(link):
    resp = session.get(base_url + link)
    
    while resp.status_code == 403:
        time.sleep(1)
        resp = session.get(base_course_url)

    resp.html.render(wait=1, scrolldown=True)
    
    for recipe_block in resp.html.find('.recipe-block > a')[:5]:
        recipe_link = recipe_block.attrs.get('href', None)
        print(f"getting recipe {recipe_link}")

        if recipe_link:
            crawl_recipe(recipe_link)
            time.sleep(1)
                
def crawl_site():
    resp = session.get(base_course_url)

    while resp.status_code == 403:
        time.sleep(1)
        resp = session.get(base_course_url)

    links = list(filter(lambda x: x.startswith('/recipes/category/course/'), resp.html.links))

    for link in links[:3]:
        crawl_category_page(link) 
        

print(f"Starting to crawl {base_url}")
crawl_site()