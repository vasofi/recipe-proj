import time 
from base_crawler import BaseCrawler


class GordonRamsayCrawler(BaseCrawler):
    page_path = "gr/recipes/"
    base_url = f"https://www.gordonramsay.com"
    recipe_count = 0

    def crawl_recipe(self, link):
        recipe = self.request_link(link)
        ingredients_list = []

        for ingredient in recipe.html.find('ul.recipe-division > li'):
            ing_txt = ingredient.text.lower() 
            
            if "salt" in ing_txt and "and" in ing_txt and "pepper" in ing_txt:
                ing_parts = ing_txt.split("and")
            else:
                ing_parts = [ing_txt]

            for ing in ing_parts:
                ing_name = self.handle_ingredient(ing)

                if ing_name:
                    ingredients_list.append(ing_name)   

        return ingredients_list
                
    def crawl_page(self, response):
        recipe_items = response.html.find('.item.recipe') 

        for item in recipe_items:
            recipe_title = item.find('h2', first=True).text
            recipe_categories = [x.text for x in item.find('ul.categories > li')]
            recipe_link = ''.join([self.base_url, item.find('a', first=True).attrs.get('href')])
            ingredients_list = self.crawl_recipe(recipe_link)
            print(', '.join([recipe_link, recipe_title, '|'.join(recipe_categories), '|'.join(ingredients_list)]))

    def crawl_site(self):
        while self.page_path is not None and self.recipe_count < 96:
            resp = self.request_link('/'.join([self.base_url, self.page_path]))     
            self.crawl_page(resp)   
            load_more = resp.html.find('a.load-more-link', first=True)

            if not load_more:
                self.page_path = None
            else:
                self.page_path = load_more.attrs.get('href')
