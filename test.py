# -*- coding: utf-8 -*-

import utils as ut
import re

import numpy as np
from scipy import sparse

from collections import Counter

from pprint import pprint

import settings

from utils import Watcher

length = 10000
disp = Watcher(length)
for index in range(0, length):
    disp.display_load(index, length, "counting target_names indexes")


# print('tf-idf edge: {}'.format(settings.TF_IDF_EDGE))

print("ended")