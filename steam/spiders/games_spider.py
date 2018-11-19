# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector
from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.spiders import Rule
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

import re
import json

import utils as ut
from comments import Comments


class GamesSpider(CrawlSpider):

    name = "games"
    allowed_domains = ["store.steampowered.com"]

    start_urls = [
        'https://store.steampowered.com/games/'
    ]

    rules = (
        # Заходим в теги на главной странице и переходим на дальнейшие страницы
        Rule(
            LxmlLinkExtractor(
                restrict_css=('div.contenthub_popular_tags','a.pagebtn')
            ),
            # Используем колбэк как страницу, т.к. надо на каждой новой странице
            # находить игры
            callback="parse_page",
            follow=True
        ),
        # Заходим в сами игры
        Rule(
            LxmlLinkExtractor(
                restrict_css=(
                    'div#search_result_container',

                ),
                allow=(r'.*/app/.*')
            ),
            # Используем колбэк как страницу, т.к. надо на каждой новой странице
            # находить игры
            callback="parse_game",
            follow=True
        ),
    )

    gameCount = 0

    # Основная страница тега
    def parse_page(self, response):
        print('\n\nProcessing..\n' + response.url)

    def parse_game(self, response):
        GamesSpider.gameCount += 1

        # Парсим игру

        # Находим имя
        name = response.url.split('/')[-2]
        # Находим id
        game_id = response.url.split('/')[-3]
        print('\n\nParsing game: {}\tWith id: {}\n'.format(name, game_id))

        # Находим кол-во комментариев к игре
        self.comment_string = "https://store.steampowered.com/appreviews/%s?start_offset=0&day_range=30&start_date=-1&end_date=-1&date_range_type=all&filter=summary&language=russian&l=russian&review_type=all&purchase_type=all&review_beta_enabled=1"
        self.dest = f"data/games/{name}/"
        yield Request(self.comment_string % str(game_id), self.parse_json_comments)


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

    

    def closed(self, reason):
        print('=' * 5, GamesSpider.gameCount, '=' * 5)
        print("\n\noutputting values \n\n")
        Comments.ouput_values(Comments)
        print("Saving values")
        Comments.save_values(Comments)
        # Comments.parse_data(Comments)
