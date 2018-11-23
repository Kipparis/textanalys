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


# for i in range(1072, 1104):
#     print(chr(i))

output_str = ""
for i in range(100000, 128538):
    output_str += chr(i) + " "
    if (i % 20 == 0):
        output_str += "\n"

ut.write_html('smiles.txt', output_str)

print("A has code {}".format(ord('A')))
print("Z has code {}".format(ord('Z')))
print("a has code {}".format(ord('a')))
print("z has code {}".format(ord('z')))
print("~ has code {}".format(ord('~')))
print("φ has code {}".format(ord('φ')))
print("є has code {}".format(ord('є')))
print("▐ has code {}".format(ord('▐')))
print("⠄ has code {}".format(ord('⠄')))
print("𝐲 has code {}".format(ord('𝐲')))

print("ク has code {}".format(ord('ク')))

print("0 simbol have {} code".format(ord('0')))
print("9 simbol have {} code".format(ord('9')))

symb = 'ク'
code = ord(symb)



if code in range(65, 91) or code in range(97, 123) or code in range(126, 967) or code in range(1108, 9617) or code in range(10244, 119859):
        print("{} is in range".format(symb))


for code in range(65, 91):
        print(chr(code))
for code in range(97, 123):
        print(chr(code)) 
# for code in range(126, 967):
#         print(chr(code)) 
# for code in range(1108, 9617):
#         print(chr(code)) 
# for code in range(10244, 119859):
#         print(chr(code))


print("ended")