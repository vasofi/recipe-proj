import time 
from base_crawler import BaseCrawler


class GordonRamsayCrawler(BaseCrawler):
    page_path = "/gr/recipes/"
    base_url = f"https://www.gordonramsay.com"
    recipe_count = 0

    def crawl_recipe(self, link):
        recipe = self.request_link(link)
        ingredients_list = []

        for ingredient in recipe.html.find('ul.recipe-division > li'):
            ing_name = self.handle_ingredient(ingredient)

            if ing_name:
                ingredients_list.append(ing_name)   

        self.recipe_count +=1
        print("Recipe Link: ", link)
        print("Ingredients: ", ingredients_list) 
                
    def crawl_page(self, response):
        recipe_items = response.html.find('.item.recipe') 

        for item in recipe_items:
            recipe_title = item.find('h2', first=True).text
            recipe_categories = [x.text for x in item.find('ul.categories > li')]
            print("---------NEW RECIPE---------")
            print("Recipe Name: ", recipe_title)
            print("Recipe Categories: ", ', '.join(recipe_categories))
            self.crawl_recipe(''.join([self.base_url, item.find('a', first=True).attrs.get('href')]))


    def crawl_site(self):
        resp = self.request_link(''.join([self.base_url, self.page_path]))
        self.crawl_page(resp)
        next_page_path = resp.html.find('a.load-more-link', first=True).attrs.get('href')
        print(next_page_path)

        while next_page_path != self.page_path and self.recipe_count < 50:
            resp = self.request_link(self.base_url)
            self.crawl_page(resp)
            print(self.recipe_count)
            self.page_path = next_page_path

        print('finished crawler:', self.recipe_count)