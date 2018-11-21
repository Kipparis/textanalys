# -*- coding: utf-8 -*-


import os, sys
    
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

class Watcher:
    def __init__(self, length):
        # Считаем отступ значений для того, чтобы потребовалось вывести новый блок
        # В дальнейшем выводи если отступ преодолён и задаём новый
        self.delta = int(length / 10)
        self.length = length + 1
        self.h_edge = 0
        self.l_edge = 0
    

    def display_load(self, ind, message):
        if ind > self.h_edge or ind < self.l_edge:
            ind += 1


            numBoxes = 10
            # ind / length = count / 10
            count = int(ind * numBoxes / self.length)

            print(u'\u23f9' * count + ' ' * (numBoxes - count) + '|\t' + message)
            self.h_edge = ind + self.delta
            self.l_edge = ind - self.delta

class Log:
    def __init__(self, header):
        self.header = header
