# -*- coding: utf-8 -*-

import numpy as np
import json

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
        self.load_count()
        self.load_target_names()
        self.load_model()
        self.load_indexes()

    def process(self, text):
        print("(processing text in PipeLine)")

        self.features = self.split_on_features(text)
        self.cnt = Counter(self.features)

        # подсчитываем значени delta tf - idf
        features_count = len(self.features)
        for _ in range(0, features_count):
            feature = self.features[_]
            if feature not in self.features_count:
                self.values[feature] = 0
            else:
                if self.features_count[feature]['pos'] == 0: self.features_count[feature]['pos'] = 0.1
                if self.features_count[feature]['neg'] == 0: self.features_count[feature]['neg'] = 0.1

                self.values[feature] = self.cnt[feature] * log10(PipeLine.comments_count['neg_comm'] * self.features_count[feature]['pos']) / (PipeLine.comments_count['pos_comm'] * self.features_count[feature]['neg'])
            

        # Создаём строку с фичами
        row = np.zeros(shape = (1, len(self.target_names)))


        # Для каждой фичи находим соответствующий индекс
        for feature in self.features:
            # Если фича пустая, пропускаем
            if feature == '':
                continue

            # чтобы быстро начать поиск находим стартовый индекс из словаря
            first_letter = feature
            if first_letter not in self.indexes:
                continue
            start_index = int(self.indexes[first_letter].split(':')[0])
            end_index = int(self.indexes[first_letter].split(':')[-1])

            for i in range(start_index, end_index):
                if self.target_names[i] == feature:
                    # добавляем в соответствующий индекс
                    
                    row[1, i] = self.values[feature]

        # Делаем предсказание для этой строчки
        grade = int(self.model.predict(row))
        print(self.model.predict(row))
        if grade == 1:
            print(">positive")
        else:
            print(">negative")
                            



    def split_on_features(self, text):
        features = []

        features = text.split(' ')

        for i in range(1, len(features)):
            features.append(features[i-1] + " " + features[i])

        return features

    def load_count(self):
        with open('data/words_count.json', 'r', encoding='utf-8') as file:
            print("Loading words_count from json")
            self.features_count = json.load(file)
        with open('data/comments_count.json', 'r', encoding='utf-8') as file:
            print("Loading comments_count from json")
            PipeLine.comments_count = json.load(file)

    def load_target_names(self):
        # Загружаем массив с фичами
        with open('data/target_names.txt', 'r') as file:
            PipeLine.target_names = file.read().split('::|::')[:-1]

    def load_model(self):
        self.model = joblib.load('data/svc_model.sav')

    def load_indexes(self):
        # Загружаем индексы фичей
        with open('data/target_names_indexes.json', 'r', encoding='utf-8') as file:
            print("Loading target_names_indexes from json")
            self.indexes = json.load(file)