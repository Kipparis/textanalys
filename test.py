# -*- coding: utf-8 -*-

import utils as ut
import re

import numpy as np
from scipy import sparse

from collections import Counter

from pprint import pprint

import settings

from utils import Watcher

arr = np.array([
    [1,2,3],
    [4,5,6],
    [6,7,8]
])

row = np.array([[1,2,3]])

new_arr = np.r_[arr, row]

print(new_arr)
# print('tf-idf edge: {}'.format(settings.TF_IDF_EDGE))

print("ended")