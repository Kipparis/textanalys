# -*- coding: utf-8 -*-

import utils as ut
import re

strings = ["\t\t\t\t\tПользователей, посчитавших этот обзор полезным: 199\t\t\t\t\t\t\t\t\t\t\t", 
            "\t\t\t\t\tПользователей, посчитавших этот обзор полезным: 64\t\t\t\t\t\t\t\t\t\t", 
            "1 пользователь посчитал этот обзор забавным", 
            "\t\t\t\t\tПользователей, посчитавших этот обзор полезным: 6\t\t\t\t\t\t\t\t\t\t\t\t\t\t"]

numbers = ['\t\tasbalsd: 123\t\t', '\t\t\tasdas: 1\t\t', '\t\t1 asdasd\t\t', '\t\t\t1231 asdfa\t\t\t']

positive = r"полезным"
funny = r"забавным"

num = re.compile(r'[0-9]+\.?[0-9]*')

for number in numbers:
    print(num.findall(number), number)

print("ended")