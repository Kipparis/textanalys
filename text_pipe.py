# -*- coding: utf-8 -*-

import numpy as np
from scipy.sparse import lil_matrix
import json

import utils as ut

from math import log10

from collections import Counter
from sklearn.externals import joblib # Для сохранения и загрузки

class PipeLine:
    # {'фича': значение}

    features_count = {}
    comments_count = {}

    target_names = []
    target_names_indexes = {}

    values = {}

    # Все коэффиценты tf idf делать общими для всего класса
    def __init__(self):
        self.load_target_names()
        self.load_frac()
        self.load_model()
        self.load_indexes()

    def process(self, text):
        print("(processing text in PipeLine)")

        self.features = self.split_on_features(text)
        # print(self.features)

        self.cnt = Counter(self.features)
        # print(self.cnt)

        for feature in self.features:
            if feature in self.delta_frac:
                self.values[feature] = self.cnt[feature] * self.delta_frac[feature]
            else:
                self.values[feature] = 0
        # print(self.values)

        # Создаём строку с фичами
        # row = np.zeros(shape = (1, len(self.target_names)))
        row = lil_matrix((1, len(self.target_names)))
        print(row)

        print(len(self.target_names))


        # Для каждой фичи находим соответствующий индекс
        for feature in self.features:
            print("=" * 10)
            print("Current feature:\t{}".format(feature))
            # чтобы быстро начать поиск находим стартовый индекс из словаря
            first_letter = feature[0]
            print("First letter:{}".format(first_letter))
            if first_letter not in self.indexes:
                print("This letter not in indexes")
                continue
            start_index = int(self.indexes[first_letter].split(':')[0])
            end_index = int(self.indexes[first_letter].split(':')[-1])
            print("Start index: {}\tEnd index: {}".format(start_index, end_index))

            for i in range(start_index, end_index):
                curr_target_name = self.target_names[i]
                # print("Current target name:\t{}\tWith index: {}".format(curr_target_name, i))
                if curr_target_name == feature:
                    print("founded index {} for feature {}".format(i, feature))
                    # добавляем в соответствующий индекс
                    row[0, i] = self.values[feature]
                    print("value of feature: {}".format(self.values[feature]))
                    # print("Target name {} doesn't equal to {}".format(curr_target_name, feature))
            
            print("=" * 10)

        print(row)

        # Делаем предсказание для этой строчки
        # TROUBLES: не разбивает нормально на фичи 
        # print("row is: {}".format(row.todense()))

        grade = int(self.model.predict(row))
        print(self.model.predict(row))
        if grade == 1:
            print(">positive")
        else:
            print(">negative")
                            


    # ужасная игра невозможно играть много доната
    def split_on_features(self, text):
        features_l = []
        features_l = text.split(' ')

        for i in range(1, len(features_l)):
            features_l.append(features_l[i-1] + " " + features_l[i])

        features_set = set()
        for feature in features_l:
            output = ut.clear_some_sht(feature)
            if output != None:
                # Если это скрытый массив, разделяем и добавляем каждую фичу
                if "||||" in output:
                    output_list = output.split("||||")
                    if len(output_list) != 0:
                        for out in output_list:
                            if out != "":
                                features_set.add(out)
                # Если это обыная строчка, просто добавляем
                else:
                    if output != "":
                        features_set.add(output)

        # Вообще все фичи == features_l
        # Потом парсим каждую фичу и добавляем её в сет
        # После этого переводим сет в нормальный список своих фичей
        features = list(features_set)

        return features

    def load_target_names(self):
        # Загружаем массив с фичами
        with open('data/target_names.txt', 'r') as file:
            PipeLine.target_names = file.read().split('\n::|::\n')[:-1]

    def load_model(self):
        self.model = joblib.load('data/svc_model.sav')

    def load_indexes(self):
        # Загружаем индексы фичей
        with open('data/target_names_indexes.json', 'r', encoding='utf-8') as file:
            print("Loading target_names_indexes from json")
            self.indexes = json.load(file)

    def load_frac(self):
        with open('data/delta_tf_idf_frac.json', 'r', encoding='utf-8') as file:
            print("Loading delta frac from json")
            self.delta_frac = json.load(file)
            