import django
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()

from recipes.crawlers.jamie_oliver_scraper import JamieOliverScraper
from recipes.crawlers.gordon_ramsay import GordonRamsayCrawler

print("Link", "Recipe Title", "Recipe Categories", "Ingredients List")
JamieOliverScraper().crawl_site()
GordonRamsayCrawler().crawl_site()
