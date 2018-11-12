# -*- coding: utf-8 -*-

import utils as ut
import re

import numpy as np
from scipy import sparse

from collections import Counter

from pprint import pprint

import settings


arr = np.array([[1,2,3]])

arr = np.r_[arr, np.array([[4,5,6]])]
arr = np.r_[arr, np.array([[7,8,9]])]

print(arr)
# print('tf-idf edge: {}'.format(settings.TF_IDF_EDGE))

print("ended")