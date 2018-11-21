# -*- coding: utf-8 -*-

import json

import utils as ut
import re

import numpy as np
from scipy import sparse

from collections import Counter

from pprint import pprint

import settings

from utils import Watcher


reg = r'\S+{n}\S*'

reg = re.compile(reg)

inp_str = "asdf {n} asdf {n}asdf adadsf{n}asdf brake{n}"
inp_str2 = "asd asdf asd asd asdf"

print(reg.findall(inp_str2))

print(len(reg.findall(inp_str)) == 0)

print("ended")