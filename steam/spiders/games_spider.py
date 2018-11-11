import scrapy
from scrapy.http import Request
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.spiders import Rule

import re
import json

import utils as ut
from comments import Comments


# TODO: Добавить список в главный класс
# TODO: Сделать управление программой из главного класса, т.е. либо закачивать новые данные затем использовать их
# либо сразу использовать готовый файл
class GamesSpider(scrapy.Spider):
    name = "games"

    start_urls = [
        # 'https://store.steampowered.com/explore/new/',
        # 'https://store.steampowered.com/genre/Free%20to%20Play/',
        # 'https://store.steampowered.com/search/?filter=topsellers',
        # 'https://store.steampowered.com/vr/',
        # 'https://store.steampowered.com/genre/Early%20Access/',
        'https://store.steampowered.com/games/'
    ]

    # Создаём правило перехода по кнопке
    # Rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//div[@class="paged_items_paging_controls"]/span[@id="NewReleases_btn_next"]',)), callback="parse", follow= True),)

    def parse(self, response):
        print("\n\nparse opened\n\n")
        page = response.url.split("/")[-2] # Получается имя игры
        filename = 'data/%s.html' % page
        ut.write_html(filename, response.body)
        self.log('Saved file %s' % filename)

        print("-------------------------")

        for gameUrl in response.css('div.tab_content a').xpath('@href').extract():
            game = gameUrl.split("/")[-2]
            gameId = gameUrl.split("/")[-3]

            if ('pack' in game.lower()):
                continue # Если это какой то пак, тупо скипаем

            gs = GameSpider(game, gameId)            
            yield Request(gameUrl, gs.parse_game)

        # Если находим стрелочку вправо, жмём на неё и опять вызываем эту же функцию



    def closed(self, reason):
        print("\n\noutputting values \n\n")
        Comments.ouput_values(Comments)
        print("Saving values")
        Comments.save_values(Comments)
        # Comments.parse_data(Comments)

class GameSpider:
    comm = Comments()

    comment_string = "https://store.steampowered.com/appreviews/%s?start_offset=0&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=russian&l=russian&review_type=all&purchase_type=all&review_beta_enabled=1"

    def __init__(self, name, id):
        self.name = name
        self.id = id

        self.dest = f"data/games/{name}/"


    def parse_game(self, response):

        filename = self.dest + "main_page.html"
        ut.write_html(filename, response.body)

        print("\nvvvvvvvvvvvvvvvvvvvvvv")
        print("Parsing game\t{}\tid\t{}".format(self.name, self.id))

        print("Starting request : ", self.comment_string % str(self.id))
        yield Request(self.comment_string % str(self.id), self.parse_json_comments)

        print("^^^^^^^^^^^^^^^^^^^^^^\n")

    def parse_json_comments(self, response):

        print("==============\nstart parsing json\n===============")

        num = re.compile(r'[0-9]+\.?[0-9]*') # Регулярное выражение для определения числа


        data = json.loads(response.body)
        ut.write_html(self.dest + "comments.html", data['html'])

        html = data['html'].replace('<br>', '\n') # Заменяем для целостности комента

        selector = Selector(text=html)
        selector.remove_namespaces()

        output = ""
        
        # Используем регулярное выражение для получения только полных комментариев
        review_boxes = selector.xpath("//div[re:test(@class, '\Areview_box+\s\Z')]")
        for review in review_boxes:
            output += "\n=======================\n"

            if review.css('div.persona_name') is None:
                continue # Если такого не существует пропускаем

            persona_name = review.css('div.persona_name')
            
            if persona_name.css('a::text').extract_first() is None:
                name = "i have to search in span"
                continue
            else:
                name = str(persona_name.css('a::text').extract_first())

            if persona_name.css('a::attr(href)').extract_first() is None:
                url = "have to search in another place"
                continue
            else:
                url = str(persona_name.css('a::attr(href)').extract_first())

            if url != "None" and url is not None:
                person_id = url.split('/')[-2]
            else:
                person_id = "Doesn't exist"

            if review.css('div.num_owned_games a::text').extract_first() is None:
                num_owned_games = "Didn't find"
                continue
            else:
                num_owned_games = str(review.css('div.num_owned_games a::text').extract_first()).split(' ')[-1]
                num_owned_games = num_owned_games.replace(',', '')
                num_owned_games = num_owned_games.replace('.', '')

            if review.css('div.num_reviews a::text').extract_first() is None:
                num_reviews = "Didn't find"
                continue
            else:
                num_reviews_text = review.css('div.num_reviews a::text').extract_first().strip()
                if num.match(num_reviews_text):
                    num_reviews = (num.findall(num_reviews_text))[0].strip()
                    num_reviews = num_reviews.replace(',', '')
                    num_reviews = num_reviews.replace('.', '')
                else:
                    num_reviews = "0"    


            if review.xpath('.//div[contains(@class, "title ellipsis")]/text()').extract_first() is None:
                grade = "Didn't find"
                continue
            else:
                grade = review.xpath('.//div[contains(@class, "title ellipsis")]/text()').extract_first()
                if grade == "Рекомендую":
                    grade = "1"
                else:
                    grade = "0"

            if review.xpath('.//div[contains(@class, "hours ellipsis")]/text()').extract_first() is None:
                hours = "Didn't find"
                continue
            else:
                hours = review.xpath('.//div[contains(@class, "hours ellipsis")]/text()').extract_first()
                hours = hours.split(' ')[-2].replace('.', '')
                hours = hours.replace(',', '')

            if review.css('div.vote_info::text').extract_first() is None:
                num_useful = "Didn't find"
                num_funny = "Didn't find"
                continue
            else:
                useful = "Not found"
                funny = "Not found"

                num_useful = '0'
                num_funny = '0'

                votes_info = review.css('div.vote_info::text').extract()
                
                for _ in votes_info:
                    votes = _.splitlines()
                    for vote in votes:
                        if 'полезным' in vote:
                            useful = vote.strip()
                            num_useful = num.findall(useful)[0].strip()
                        elif 'забавным' in vote:
                            funny = vote.strip()
                            num_funny = num.findall(funny)[0].strip()                    
                        

                
            if review.css('div.content::text').extract_first() is None:
                text = "None"
                continue
            else:
                text = review.css('div.content::text').extract_first()

            num_reviews = num.findall(num_reviews_text)[0]


            output += "Name\tis:\t{}\n".format(name)
            output += "Url\tis:\t{}\n".format(url)
            output += "Id \tis:\t{}\n".format(person_id)
            output += "Owned games:\t{}\n".format(num_owned_games)
            output += "Num reviews:\t{}\n".format(num_reviews)
            output += "Grade\tis:\t{}\n".format(grade)
            output += "Ingame hours:\t{}\n".format(hours)
            
            output += "People think it helpful:\t{}\n".format(num_useful)
            output += "People think it funny:\t\t{}\n".format(num_funny)

            # output += "Text:\n{}\n".format(text)


            Comments.add_comment(Comments,
                            text, num_owned_games, num_reviews, grade,
                                hours, num_useful, num_funny)

            output += "=======================\n"           


        ut.write_html(self.dest + "reviewers.txt", output)

        # output = ""
        # comments = selector.css('div.review_box').css('div.content::text').extract()
        # for comment in comments:
        #     comment = comment.strip()
        #     if not comment:
        #         continue    # Пропускаем если строчка пустая
        #     output += "\n=============================\n"
        #     output += comment
        #     output += "\n=============================\n"
        

        
        # ut.write_html(self.dest + 'comments.txt', output)
        
        print("==============\nended parsing json\n===============")


        # TODO: Используя json симитировать ajax запросы для паука
        # https://store.steampowered.com//userreviews/ajaxgetvotes/
        # TODO: Если это происходит в несколько этапов, узнать основу
        # страницы и делать в цикле for несколько вызовов
        # TODO: Скачивать всё в json файл
        # TODO: Создавать директории для каждой игры для упрощённого просмотра
        # TODO: Сделать лог для отслеживания точечных ошибок
        # TODO: Парсить ревьюверов в json | xml

    