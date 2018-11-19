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

with open('data/target_names.txt', 'r') as file:
    target_names = file.read().split('\n')

print(target_names)

print("ended")