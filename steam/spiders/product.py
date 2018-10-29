import scrapy
import smart_getenv

from scrapy.contrib.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider



class ProductSpider(CrawlSpider):

    name = 'products'

    start_urld = ['http://store.steampowered.com/search/?sort_by=Released_DESC']

    allowed_domains=["steampowered.com"]

    # По каким правилам паучки переходят на ссылки
    rules = [
        Rule(
            LinkExtractor(

                allow='/app/(.+)/',

                restrict_css='#search_result_container'),
            
            callback='parse_product'),
            
        Rule(
            LinkExtractor(
                allow='page=(\d+)',

                restrict_css='.search_pagination_right'
            )
        )
    ]

def parse_product(self, response):
    return {
        'app_name': response.css('.apphub_AppName ::text').extract_first(),
        
        'specs': response.css('.game_area_details_specs a ::text').extract()
    }
