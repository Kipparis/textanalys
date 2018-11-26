# -*- coding: utf-8 -*-


import os, sys
import re
    
def write_html(path, html):

    print("writing html")    
    
    pathDir = path.split('/')

    name = pathDir[-1]
    pathDir.pop()[-1]

    createPath = ""
    
    for fold in pathDir:
        createPath += fold + "/"
        if not os.path.exists(createPath):
            os.mkdir(createPath)


    if (os.path.exists(createPath + name)):
        os.remove(createPath + name)
    if isinstance(html, str):
        with open(createPath + name, '+w') as file:
            file.write(html)
    else:
        with open(createPath + name, "wb") as file:
            try:
                file.write(html)
            except:
                print("Error while writing ", html, "in", createPath + name)


def path_exists(path):
    return(os.path.exists(path))


# Если фича состоит из неправильных букв, возвращает None
# Если там разделитель между словами, возвращает слово1||слово2
# Если там разделитель в начале или в конце слова просто убирает его и возвращает
# TODO: сделать проверку чтобы фича не состояла из одного числа
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
    stupid_symbol = re.compile(r'\S+([.,\-()!:?"\']|\{n\})+\S+')
    only_numb = re.compile(r'\A[1-9]+\Z')
    string_symb = ".,-:()!\"?\'"
    symbols = list(string_symb)
    symbols.append('{n}')

    if len(only_numb.findall(feature)) != 0:
        return None

    if len(stupid_symbol.findall(output)) != 0:
        for symb in symbols:
            if symb in output:
                # TODO: заканчивание предложения - удаляем, также чекаем на фичу из одних цифр
                output = output.split(symb)[0] + '||||' + output.split(symb)[-1].strip()
    else:
        for symb in symbols:
            if symb in output:
                output = output.replace(symb, '').strip()

    # Если там присутствуют английские или какие то ебучие буквы, ремуваем
    for letter in output:
        code = ord(letter)
        if letter == "|":
            continue
        elif not (((code >= 1040) and (code <= 1104)) or ((code >= 48) and (code <= 58)) or code == 32):
            return None
    return output


class Watcher:
    def __init__(self, length):
        self.numBoxes = 20
        # Считаем отступ значений для того, чтобы потребовалось вывести новый блок
        # В дальнейшем выводи если отступ преодолён и задаём новый
        self.delta = int(length / self.numBoxes)
        self.length = length + 1
        self.h_edge = 0
        self.l_edge = 0
    

    def display_load(self, ind, message):
        if ind > self.h_edge or ind < self.l_edge:
            ind += 1

            count = int(ind * self.numBoxes / self.length)

            print(u'\u23f9' * count + ' ' * (self.numBoxes - count) + '|\t' + message)
            self.h_edge = ind + self.delta
            self.l_edge = ind - self.delta

class Log:
    def __init__(self, header):
        self.header = header
