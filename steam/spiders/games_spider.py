import json
from scrapy.selector import Selector

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request

import utils as ut

class GamesSpider(scrapy.Spider):
    name = "games"

    start_urls = [
        'https://store.steampowered.com/explore/new/'
    ]

    def parse(self, response):
        print("\n\nparse opened\n\n")
        page = response.url.split("/")[-2] # Получается имя игры
        filename = 'data/%s.html' % page
        ut.write_html(filename, response.body)
        self.log('Saved file %s' % filename)

        print("-------------------------")

        for gameUrl in response.css('div.tab_content a').xpath('@href').extract():
            game = gameUrl.split("/")[-2]

            if ('pack' in game.lower()):
                continue # Если это какой то пак, тупо скипаем
            
            # print("Found game: {}".format(game))
            # print("Url is: {}".format(gameUrl))
            # print("vvvvvvvvvvvvvvvvvvvvvvv")

            yield Request(gameUrl, GameSpider.parse_game)
        # tab_content
        # response.css('img').xpath('@src').extract()

    def parse_game(self, response):
        game = response.request.url.split('/')[-2]
        app_id = response.request.url.split('/')[-3]
        print("\nvvvvvvvvvvvvvvvvvvvvvv")
        print("Parsing game\t{}\tid\t{}".format(game, app_id))


        # TODO: Используя json симитировать ajax запросы для паука
        # https://store.steampowered.com//userreviews/ajaxgetvotes/
        # TODO: Если это происходит в несколько этапов, узнать основу
        # страницы и делать в цикле for несколько вызовов
        # TODO: Скачивать всё в json файл
        # TODO: Создавать директории для каждой игры для упрощённого просмотра
        

# https://store.steampowered.com/appreviews/294100?start_offset=0&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=russian&l=russian&review_type=all&purchase_type=all&review_beta_enabled=1&summary_num_positive_reviews=22733&summary_num_reviews=23376
        # first_comment = response.css('div.leftcol').css('div.content::text').extract_first()
        # print("First comment is {}".format(first_comment))

# https://store.steampowered.com/appreviews/294100?start_offset=0&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=russian&l=russian&review_type=all&purchase_type=all&review_beta_enabled=1
# https://store.steampowered.com/appreviews/885810?start_offset=0&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=russian&l=russian&review_type=all&purchase_type=all&review_beta_enabled=1

        request_string = "https://store.steampowered.com/appreviews/%s?start_offset=0&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=russian&l=russian&review_type=all&purchase_type=all&review_beta_enabled=1"
        filename = f'data/games/{game}/{game}.html'
        ut.write_html(filename, response.body)
        

        print("Starting request : ", request_string % str(app_id))

        # Request(request_string % str(app_id), self.parse_game, self.parse_json)

        print("^^^^^^^^^^^^^^^^^^^^^^\n")
    
    # def parse_json(self, response):
    #     data = json.loads(response.body)

    #     with open('/data/games/keys.json', encoding='utf-8') as fh:
    #         data = json.load(fh)

    #     print(data)

# >>> fetch("https://store.steampowered.com/appreviews/294100?start_offset=0&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=russian&l=russian&review_type=all&purchase_type=all&review_beta_enabled=1")
# data = json.loads(response.body)
# html = data['html']

class GameSpider():

    comment_string = "https://store.steampowered.com/appreviews/%s?start_offset=0&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=russian&l=russian&review_type=all&purchase_type=all&review_beta_enabled=1"

    def parse_game(self, response):

        game = response.request.url.split('/')[-2]
        app_id = response.request.url.split('/')[-3]
        print("\nvvvvvvvvvvvvvvvvvvvvvv")
        print("Parsing game\t{}\tid\t{}".format(game, app_id))

        print("Starting request : ", self.comment_string % str(app_id))

        print("^^^^^^^^^^^^^^^^^^^^^^\n")