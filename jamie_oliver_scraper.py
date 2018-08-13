from base_crawler import BaseCrawler
import time

class JamieOliverScraper(BaseCrawler):
    base_url = "https://www.jamieoliver.com"
    base_course_url = "https://www.jamieoliver.com/recipes/category/course/"
    recipe_count = 0

    def crawl_recipe(self, link):
        '''
            This utillity receive a link to a recipe and prints the recipe's name,
            recipe's categories(Italian, dinner, etc.) and the recipe's ingredients
        '''
        recipe_resp = self.request_link(self.base_url + link)
        try:
            recipe_resp.html.render()
        except:
            return

        recipe_title = recipe_resp.html.find('h1', first=True).text

        while recipe_title == "403 Forbidden":
            time.sleep(5)
            recipe_resp = self.request_link(self.base_url + link)

            try:
                recipe_resp.html.render()
                recipe_title = recipe_resp.html.find('h1', first=True).text
            except:
                time.sleep(3)

            
            
        blacklisted_categories = ["book", "jamie cooks italy", "jamie magazine"]
        recipe_tags = []
        
        for tag in recipe_resp.html.find('.tags-list > a'):
            category = tag.text

            if category:
                category = category.strip().strip(',')

                if category.lower() not in blacklisted_categories:
                    recipe_tags.append(category)
        
        # Checking if the page has duplicate ingredients list
        metric_ingred_list = recipe_resp.html.find('ul.ingred-list.metric')

        if metric_ingred_list:
            ingredients_html = recipe_resp.html.find('ul.ingred-list.metric > li')
        else:
            ingredients_html = recipe_resp.html.find('ul.ingred-list > li')
        
        ingredients_list = []

        for ingredient in ingredients_html:
            ing_name = self.handle_ingredient(ingredient.text)

            if ing_name:
                ingredients_list.append(ing_name)

        if ingredients_list:
            self.recipe_count += 1
            print('-----------------------------NEW RECIPE-----------------------------')
            print("Recipe Link: ", link)
            print("Recipe name: ", recipe_title)
            print("Recipe categories: ", ', '.join(recipe_tags))
            print("Ingredients: ", ingredients_list)

    def crawl_category_page(self, link):
        resp = self.request_link(self.base_url + link)
        try:
            resp.html.render(wait=1, scrolldown=True)
        except:
            time.sleep(3)
            return
        
        for recipe_block in resp.html.find('.recipe-block > a'):
            recipe_link = recipe_block.attrs.get('href', None)

            if recipe_link:
                self.crawl_recipe(recipe_link)
                time.sleep(1)
                        
    def crawl_site(self):
        resp = self.request_link(self.base_course_url)

        while not resp:
            time.sleep(5)
            resp = self.request_link(self.base_course_url)

        links = list(filter(lambda x: x.startswith('/recipes/category/course/'), resp.html.links))

        for link in links[:3]:
            self.crawl_category_page(link) 

        print('finished crawler:', self.recipe_count)