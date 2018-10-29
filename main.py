# -*- coding: utf-8 -*-

import os

import requests # download html

# url = https://store.steampowered.com/app/219740/  # Dont_Starve/

# DATA_APP = "data/apps/"

# app_id = 219740
# url = 'https://store.steampowered.com/app/{}'.format(app_id)



# r = requests.get(url)

# # print(r.text.encode('utf-8'))

# if not os.path.exists("data/apps/Dont_Starve"):
#     os.makedirs("data/apps/Dont_Starve")

# with open('data/apps/Dont_Starve/commun_page.html', 'wb') as output_file:
#     output_file.write(r.text.encode('utf-8'))


# import mechanicalsoup

# gamename = 'super meat boy'

# # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
# browser = mechanicalsoup.StatefulBrowser(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0')

# # browser.open("https://store.steampowered.com/search/?term=")
# browser.open("https://store.steampowered.com/")
# print("Current url:", browser.get_url())

# # game search
# browser.select_form('div[class="searchbox"]')
# browser.get_current_form().print_summary()

# browser['term'] = gamename
# browser.get_current_form().print_summary()

# response = browser.submit_selected()
# print(browser.get_url())

# # checkbox on "games only"
# # browser.select_form('div[id="narrow_category1"]')
# # browser.get_current_form().print_summary()

# # browser["category1"] = "Games"
# # browser.launch_browser()

import scrapy
