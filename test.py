# -*- coding: utf-8 -*-

import utils as ut
import re

from collections import Counter

data = "make this make that make something else".split(" ")
# Создаём объект класса каунтер и передаём ему как аргумент массив

cntr = Counter(data)

print(cntr)


print("ended")