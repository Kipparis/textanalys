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

def clear_some_sht(feature):
    # Если послали полную хуйню, возвращаем пустоту => там понимаем что убираем всё
    output = feature.strip().lower()
    if output == '':
        return None
    # циклим убираем все запятые, сокращаем восклицательные знаки, вопросительные знаки, если точка тогда возвращаем первый элемент либо просто убираем точку
    # если встречается {n} сокращаем как точку.
    isChanged = True
    while isChanged:
        first_letter = output[0]
        code = ord(first_letter)
        if '{n}{n}' in output:
            output = output.replace('{n}{n}', '{n}')
        elif '!!' in output:
            output = output.replace('!!', '!')
        elif '??' in output:
            output = output.replace('??', '?')
        elif ',,' in output:
            output = output.replace(',,', ',')
        elif '..' in output:
            output = output.replace('..', '.')
        elif '\"\"' in output:
            output = output.replace('\"\"', '\"')
        elif '\'\'' in output:
            output = output.replace('\'\'', '\'')
        else:
            isChanged = False
    # проверяем такие случаи как text.text    text{n}text    text,text    text?!"'tetxt ( вроде можно создать регурярку используя [] для задания множествас) 
    stupid_symbol = re.compile(r'\S+([.,\-()!?"\']|\{n\})+\S+')
    string_symb = ".,-()!\"?\'"
    symbols = list(string_symb)
    symbols.append('{n}')
    if len(stupid_symbol.findall(output)) != 0:
        for symb in symbols:
            if symb in output:
                output = output.split(symb)[0] + '||||' + output.split(symb)[-1].strip()
                print("Split by {} and return {}".format(symb, output))
    else:
        for symb in symbols:
            if symb in output:
                output = output.replace(symb, '').strip()
                print("Remove and return {}".format(symb))
    # Если там присутствуют английские или какие то ебучие буквы, ремуваем
    for letter in output:
        code = ord(letter)
        # print("Outputting: {}\tCode: {}".format(letter, code))
        if letter == "|":
            continue
        elif not (((code >= 1040) and (code <= 1104)) or ((code >= 48) and (code <= 58))):
            print(code)
            print("{} not in given range".format(chr(code)))
            return None
    return output

spacees = input("type your feature: ")
output = clear_some_sht(spacees)
if output != None:
    print("output contains something")
    if "||||" in output:
        output = output.split("||||")
        print("output is: {}".format(output))
        for out in output:
            if out == "": output.remove(out)


if output is None:
    print("useless string")
else:
    print("parsing string: {}\toutput is: {}".format(spacees, output))



# print("А has code {}".format(ord('А')))
# print("Я has code {}".format(ord('Я')))
# print("а has code {}".format(ord('а')))
# print("я has code {}".format(ord('я')))


# print("A has code {}".format(ord('A')))
# print("Z has code {}".format(ord('Z')))
# print("a has code {}".format(ord('a')))
# print("z has code {}".format(ord('z')))
# print("~ has code {}".format(ord('~')))
# print("φ has code {}".format(ord('φ')))
# print("є has code {}".format(ord('є')))
# print("▐ has code {}".format(ord('▐')))
# print("⠄ has code {}".format(ord('⠄')))
# print("𝐲 has code {}".format(ord('𝐲')))
# print("! has code {}".format(ord('!')))
# print("/ has code {}".format(ord('/')))
# print("0 has code {}".format(ord('0')))
# print("9 has code {}".format(ord('9')))

# print("  has code {}".format(ord(' ')))
# print("І has code {}".format(ord('І')))

# print("А has code {}".format(ord('0')))
# print("Я has code {}".format(ord('9')))

# print("а has code {}".format(ord('0')))
# print("я has code {}".format(ord('9')))

symb = 'ク'
code = ord(symb)



# if code in range(65, 91) or code in range(97, 123) or code in range(126, 967) or code in range(1108, 9617) or code in range(10244, 119859):
        # print("{} is in range".format(symb))




print("ended")