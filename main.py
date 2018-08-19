from jamie_oliver_scraper import JamieOliverScraper
from gordon_ramsay import GordonRamsayCrawler

print("Link", "Recipe Title", "Recipe Categories", "Ingredients List")
GordonRamsayCrawler().crawl_site()
JamieOliverScraper().crawl_site()