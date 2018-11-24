# -*- coding: utf-8 -*-

# Для сохранения
import csv
import json

# Для машинного обучения
import numpy as np
from scipy import sparse

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn import svm
from sklearn.externals import joblib # Для сохранения
from sklearn.naive_bayes import MultinomialNB

# Для более быстрого написания в файл
import utils as ut
# для того чтобы имортить переменный настроек
import settings

from collections import Counter
from math import log10

from pprint import pprint

from utils import Watcher

import re

# TODO: Как нибудь с помощью видеокарты ускорить подсчёт этих значений

class Comments:
    log = False

    comments = []


    positive_comments = []
    negative_comments = []

    # {"фича": значение}
    delta_tf_idf_frac = {}
    idf = {}

    target_names = []
    target_names_dict = {}
    

    # 'имя фичи' : {'all': $всего, 'pos': $в_позитивных, 'neg': $в_негативных}
    features_count = {}

    stupid_comments = ''

    owned = []
    reviews = []
    grade = []
    ingame_hours = []
    helpful = []
    funny = []

    output = ""

    texts = []

    def __init__(self):
        print("Initing comments")

    # TODO: Добавили поле game тепер надо создать в каждой папке игры словарь со словами и их значениями
    # TODO: В одном файле создать поля игра:никпользователя:остальныеполя , классе комментариев сделать то же самое
    # в последующем, когда комментарий создан но значения не подсчитаны мы просто обращаемся к значениям из файла

    def add_comment(self, text, owned, reviews, 
                    grade, ingame_hours, helpful, funny):
        
        # text = text.replace('\t', '').replace('\n', '').strip()

        if text.replace('\t', '').replace('\n', '').strip() == '':
            return

        self.owned.append(owned)
        self.reviews.append(reviews)
        self.grade.append(grade)
        self.ingame_hours.append(ingame_hours)
        self.helpful.append(helpful)
        self.funny.append(funny)
        # Заменяем все управляющие символы для того чтобы всё было в одну строчку
        self.texts.append(text.replace("\t", "").replace("\n", "{n}").strip())

        print('>- Edding comment -<')

    def ouput_values(self):
        print("Comments count:\t{}".format(len(self.grade)))

        print("Grade:\n{}".format(self.grade))
        print("Owned:\n{}".format(self.owned))
        print("Reviews:\n{}".format(self.reviews))
        print("Hours:\n{}".format(self.ingame_hours))
        print("Helpful:\n{}".format(self.helpful))
        print("Funny:\n{}".format(self.funny))
        
        # print("Comments:\n{}".format(self.texts))

    # Сохраняем в файл data/data.csv 
    def save_values(self):
        print('\n\nsaving values\n\n')

        path = 'data/data.csv'
        with open(path, "+w") as csv_file:
            writer = csv.writer(csv_file, delimiter=':') # Должна быть в длинну одним символом
            for comment_ch in zip(self.grade, self.owned, self.reviews,
                                self.ingame_hours, self.helpful, self.funny,
                                self.texts):
                writer.writerow(comment_ch)
                if self.log: print(comment_ch)

        print('\n\nended saving data\n\n')

    # Загружаем данные из файла data/data.csv с разделителем :
    def load_values(self):
        print('\n\nLoading values\n\n')

        with open("data/data.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if self.log: print("".join(row))
                comm = "".join(row).split(':', 6)
                if self.log: print("Variable comm\n",comm)
                self.grade.append(comm[0])
                self.owned.append(comm[1])
                self.reviews.append(comm[2])
                self.ingame_hours.append(comm[3])
                self.helpful.append(comm[4])
                self.funny.append(comm[5])
                self.texts.append(comm[6])



        if self.log: Comments.ouput_values(Comments)

    # Для каждого текста посчитать внутренние слова
    # Создать массив положительных комментариев
    # Массив отрицательных цомментариев

    # If the number of features is much greater than the number of samples, 
    # avoid over-fitting in choosing Kernel functions 
    # and regularization term is crucial.
    def parse_data(self):
        X = self.data
        print("X shape {}".format(X.shape))
        y = self.grades

        reg = 1.0 # Параметр регуляризации SVM
        print("C value is: {}".format(reg))
        clf = svm.SVC(kernel=settings.KERNEL, C=reg, random_state=2)
        # clf = MultinomialNB() # наивный байесовский классификатор

        scores = cross_val_score(clf, X, y, cv=3, n_jobs=-1)
        print(scores)
        print("Score.mean:\t{}".format(scores.mean()))
        print("Scores.std:\t{}".format(scores.std() * 2))
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

        final_model = clf.fit(X, y)
        Comments.model = final_model

        # Сохраняем модель
        filename = 'data/svc_model.sav'
        print("Saving model into:\t{}".format(filename))
        joblib.dump(final_model, filename)


        # print("Точность обучения: {}".format(np.mean(y_test == y_pred)))


    def process_data(self):
        print("#" * 10, "Processing data", "#" * 10)

        grades = []
        # Создаём классы комментариев
        for raw in zip(self.grade, self.owned, self.reviews,
                self.ingame_hours, self.helpful, self.funny, self.texts):
            # Передаём в новый коммент текст и оценку
            comm = Comment(raw[0], raw[-1])
            self.comments.append(comm)
            grades.append(comm.grade)
            if raw[0] == "1":
                Comments.positive_comments.append(comm)
            else:
                Comments.negative_comments.append(comm)

        # Сохраняем кол-во позитивных и негативных комментов
        
        comments_count = {
            "pos_comm": len(Comments.positive_comments),
            "neg_comm": len(Comments.negative_comments)
            }
        with open('data/comments_count.json', '+w') as file:
            json.dump(comments_count, file)

        Comments.grades = np.array(grades)
        np.save("data/grades.npy", Comments.grade)
        
        count = 1
        if ut.path_exists('data/words_count.json'):
            with open('data/words_count.json', 'r', encoding='utf-8') as file:
                print("Loading words_count from json")
                Comments.features_count = json.load(file)
                count = 0

        # Подсчитываем для каждого коммента вектор признаков
        # from utils import Watcher следить за прогрессом
        Comments.stupid_comments = ''

        reg = r'\S+{n}\S+'
        # Перенести этот компайл над всеми комментами, а внутри использовать готовый
        Comment.useless_ns = re.compile(reg)
        reg = r'\S+,\S+'
        Comment.split_comma = re.compile(reg)

        reg = r'.+\..+'
        Comment.dot_in_center = re.compile(reg) # Точка посередине фичи

        wt = Watcher(len(self.comments))
        for comm in self.comments:
            wt.display_load(self.comments.index(comm), "making vector")
            comm.make_vector()
            # Подсчитываем кол-во фичей в этом комменте и добавляем в общую кучу
            if count: comm.count() # Подсчитываем кол-во фичей во всех комментах


        if not ut.path_exists('data/words_count.json'):
            with open('data/words_count.json', 'w') as file:
                json.dump(Comments.features_count, file, ensure_ascii=False)
        
        count = 1
        if ut.path_exists('data/idf.json'):
            with open('data/idf.json', 'r', encoding='utf-8') as file:
                print("Loading idf from json")
                Comments.idf = json.load(file)
                for comm in Comments.comments:
                    wt.display_load(Comments.comments.index(comm), "loading tf-idf")
                    comm.load_tf_idf()
                count = 0
        if count:
            for comm in self.comments:
                wt.display_load(self.comments.index(comm), "counting tf-idf")
                # Считаем и сразу удаляем ненужные слова
                comm.count_tf_idf()
                # pprint(comm.tf_idf)

        if not ut.path_exists('data/idf.json'):
            with open('data/idf.json', 'w') as file:
                json.dump(Comments.idf, file, ensure_ascii=False)

        # Выводим бесполезные слова
        ut.write_html("data/tf-idf-useless.txt", Comment.tf_idf_words)
        print("OUTPUTED DATA/TF-IDF USELESS")

        # Создаём массив таргет_нэймс
        # Подсчитываем кол-во разных слов
        target_names = set()
        for comm in self.comments:
            wt.display_load(self.comments.index(comm), "creating target names")
            # print("Comm {} from {}\tCreating target names".format(self.comments.index(comm), len(self.comments)))
            for feature in comm.features:
                target_names.add(feature)

        Comments.target_names = sorted(list(target_names))

        target_names_text = ""
        for name in Comments.target_names:
            target_names_text += name + "\n::|::\n" 
        ut.write_html("data/target_names.txt", target_names_text)

        print("Comments.target_names len is:\t{}".format(len(Comments.target_names)))

        
        wt = Watcher(len(Comments.target_names))

        # Загружаем чтобы не считать всё заново
        count = 1
        if ut.path_exists('data/target_names_indexes.json'):
            with open('data/target_names_indexes.json', 'r', encoding='utf-8') as file:
                print("Loading target_names_indexes from json")
                Comments.target_names_dict = json.load(file)
                count = 0

        
        oldLetter = ''
        endIndex = 0
        startIndex = 0
        if count:
            # Сделать по индексам, и когда нашли конечный индекс сразу смещаться на него -1
            # Делать без внутреннего цикла, а просто заводить переменную *текущая буква* и когда другая буква не равна ей просто ставить конечный индекс - новое слово
            for j in range(0, len(Comments.target_names)):
                name = Comments.target_names[j]
                if name == '':
                    continue
                wt.display_load(j, "counting indexes")
                letter = name[0]

                if letter != oldLetter:
                    endIndex = j
                    if j != 0:
                        Comments.target_names_dict[oldLetter] = str(startIndex) + ":" + str(endIndex)
                    startIndex = j
                    oldLetter = letter

                

        # Сохраняем то что сейчас написали, т.к. процесс мега трудоёмкий
        if not ut.path_exists('data/target_names_indexes.json'):
            with open('data/target_names_indexes.json', 'w') as file:
                json.dump(Comments.target_names_dict, file, ensure_ascii=False)
                print("Ended saving file")
        
        wt = Watcher(len(Comments.comments))

        # TODO: Сделать подгрузку логарифмического выражения

        # Подсчитываем delta tf - idf
        for comm in self.comments:
            wt.display_load(self.comments.index(comm), "counting delta tf-idf")
            comm.count_values()

        ut.write_html('data/delta_tf_idf_log.txt', Comments.output)

        # Сохраняем логарифмическое выражение
        with open('data/delta_tf_idf_frac.json', 'w') as file:
            json.dump(Comments.delta_tf_idf_frac, file, ensure_ascii=False)
            print("Ended saving file")


        data = sparse.lil_matrix((len(Comments.comments), len(Comments.target_names)))
        comments_len = len(Comments.comments)

        for i in range(0, comments_len):
            wt.display_load(i, "editing matrix")
            comment = Comments.comments[i]

            for feature in comment.features:
                if feature == '':
                    continue
                if feature not in comm.values:
                    continue
                
                # для каждой фичи находим индекс
                first_letter = feature[0]

                if first_letter not in Comments.target_names_dict:
                    continue

                start_ind = int(Comments.target_names_dict[first_letter].split(':')[0])
                end_ind = int(Comments.target_names_dict[first_letter].split(':')[-1])

                for j in range(start_ind, end_ind):
                    if Comments.target_names[j] == feature:
                        data[i, j] = comment.values[feature]


        Comments.data = data

        print("Data shape:\t{}".format(Comments.data.shape))
        print("Grade shape:\t{}".format(Comments.grades.shape))
        print("Target_name len:\t{}".format(len(Comments.target_names)))


        # Сохраняем массив
        # np.save("data/data.npy", Comments.data)
        # sparse.save_npz('data/data.npz', data)
        Comments.save_sparse_matrix(Comments, "data/data.npz", Comments.data)

        # np.save("data/s_data.npy", Comments.s_data)


        
    def load_data_from_file(self):
        # Comments.data = np.load('data/data.npy')
        # Comments.data = sparse.load_npz('data/data.npz')
        # Comments.s_data = np.load('data/s_data.npy')
        Comments.data = Comments.load_sparse_matrix(Comments, "data/data.npz")

        Comments.grades = np.load('data/grades.npy')
        with open('data/target_names.txt', 'r') as file:
            Comments.target_names = file.read().split('::|::')[:-1]

        

    def load_model(self):
        Comments.model = joblib.load('data/svc_model.sav')

    def count_word_in_positive(self, feature):
        if self.log: print("Counting word in positive ", feature)
        cnt = 0
        for comm in Comments.positive_comments:
            if feature in comm.features:
                cnt += 1
                
        if cnt == 0: cnt = 0.1
        return cnt

    def count_word_in_negative(self, feature):
        if self.log: print("Counting word in negative ", feature)
        cnt = 0
        for comm in Comments.negative_comments:
            if feature in comm.features:
                cnt += 1
        if cnt == 0: cnt = 0.1
        return cnt

    def count_word_in_comments(self, feature):
        if self.log: print("Counting in comments ", feature)
        cnt = 0
        for comm in Comments.comments:
            if feature in comm.features:
                cnt += 1
        if cnt == 0: cnt = 0.1
        return cnt

    def save_sparse_matrix(self, filename, x):
        x_coo = x.tocoo()
        row = x_coo.row
        col = x_coo.col
        data = x_coo.data
        shape = x_coo.shape
        np.savez(filename, row=row, col=col, data=data, shape=shape)

    def load_sparse_matrix(self, filename):
        y = np.load(filename)
        z = sparse.coo_matrix((y['data'], (y['row'], y['col'])), shape=y['shape'])
        return z
        

#######################################


class Comment:
    log = True

    tf_idf_words = ""

    # Содержит оценку, текст, и т.д. и т.п.
    def __init__(self, grade, text):
        self.grade = grade
        self.text = text

        self.features = []
        self.tf_idf = {}
        self.values = {}

    def count(self):
        # Побавляем фичи из этой фигни в общую стопку
        for feature in self.features:
            # Если этой фичи ещё нет в общем списке, добавляем с нулевыми показателями
            if feature not in Comments.features_count:
                Comments.features_count[feature] = {
                    'all': 0, 'pos': 0, 'neg': 0, 'num_all': 0, 'num_pos': 0, 'num_neg': 0
                }
            # Затем добавляем значения
            Comments.features_count[feature]['all'] += self.cnt[feature]
            Comments.features_count[feature]['num_all'] += 1
            if self.grade == 1:
                Comments.features_count[feature]['pos'] += self.cnt[feature]
                Comments.features_count[feature]['num_pos'] += 1
            else:
                Comments.features_count[feature]['neg'] += self.cnt[feature]
                Comments.features_count[feature]['num_neg'] += 1

    def make_vector(self):
        # TODO: убирать все {n} и запятые + повысить порог tf-idf
        # Создание вектора признаков
        self.features = self.text.split(' ')

        lastWord = ''
        for word in self.text.split(' '):
            if lastWord == '':
                lastWord = word
            else:
                self.features.append(lastWord + " " + word)
                lastWord = word

        # Обособлять сердечки и улыбочки всякие
        features_len = len(self.features)
        for _ in range(0, features_len):
            # print("_ is: {}\tarr len: {}".format(_, features_len))
            if _ >= len(self.features):
                break
            feature = self.features[_]

            # Приводим к нижнему регистру, чтобы при создании таргет неймс было меньше уникалок
            self.features[_] = feature.lower().strip()
            feature = feature.lower().strip()
            # print(feature)

            # Находим первую букву для дальнейших вычисления
            if feature == '':
                self.features.remove(feature)
                # print('removed cos empty')
                continue
            first_letter = feature[0]
            code = ord(first_letter)

            # Если это запятая которая отделяет два слитных слова, можем просто убрать
            if len(self.split_comma.findall(feature)) != 0:
                self.features.remove(feature)
                self.features.append(feature.split(',')[0])
                self.features.append(feature.split(',')[-1])
                # print('removed cos , in center')
            elif feature == ',':
                self.features.remove(feature)                
                # print('removed cos , in center')
            elif len(self.useless_ns.findall(feature)) != 0:
                # Если у нас где то \n мы убираем столько раз сколько надо потом добавляем граничные
                self.features.remove(feature)
                while '{n}{n}' in feature:
                    feature = feature.replace('{n}{n}', '{n}')
                self.features.append(feature.split('{n}')[0])
                self.features.append(feature.split('{n}')[-1])
                # print('removed cos reg = r"\S+{n}\S+"')
            elif (code in range(32, 1031)) or (code in range(1108, 9617)) or (code in range(10244, 119859)):
                self.features.remove(feature)
                # print(feature, "not in range")
            elif '"' in feature: # обычно если присутствует ковычка -> это название игры, которая индивидуально везде
                self.features.remove(feature)
            # (code in range(33, 48)) or
            # or (code in range(48, 58)) or
            # or (code in range(65, 91)) or
            # or (code in range(97, 123)) or
            # or (code in range(126, 967)) or
                
                # print('removed cos code in range')
            elif len(self.dot_in_center.findall(feature)) != 0:
                self.features.remove(feature)
                # print('removed cos dot in center')
            else:
                # TODO: Сначала работаю со строками, потом проверяю на удаление и так пока ничего уже нельзя будет сделать
                # TODO: Записывать старую и новую фичу

                # print('Nothing deleted')
                # print('features are:\n{}'.format(self.features))
                # print('First element of array: {}'.format(self.features[0]))
                # print('Feature: {}'.format(feature))
                # print('They equals? {}'.format(self.features[0] == feature))
                # Ни один из итемов не удалился, обрабатываем текст
                somethingChanged = True
                while somethingChanged:
                    if feature == '':
                        break
                    first_letter = feature[0]
                    code = ord(first_letter)
                    if (32 <= code < 1031) or (1108 <= code < 9617) or (10244 <= code < 119859):
                        # print(feature, "not in range")
                        self.features.remove(feature)
                        break
                    elif '{n}' in feature:
                        feature = feature.replace('{n}', '').strip()
                        self.features[_] = feature
                    elif '.' in feature:
                        feature = feature.replace('.', '').strip()
                        self.features[_] = feature
                    elif ',' in feature:
                        feature = feature.replace(',','').strip()
                        self.features[_] = feature
                    else:
                        somethingChanged = False
            features_len = len(self.features)
                      
                

        # Если список фичей пуст, удаляем этот коммент из общего списка
        if len(self.features) == 0:
            Comments.comments.remove(self)
        else:
            self.cnt = Counter(self.features)


        # Присваивание признаку его веса
        # Вес - среднее между TF-IDF и значением в словаре

    def count_tf_idf(self):
        for feature in self.features:
            # Для каждой фичи подсчитываем tf-idf
            count_in_text = self.cnt[feature]
            tf = count_in_text / len(self.text.split(' '))

            # idf = log10(len(Comments.comments) / Comments.count_word_in_comments(Comments, feature))
            idf = log10(len(Comments.comments) / Comments.features_count[feature]['num_all'])
            self.tf_idf[feature] = tf * idf

            # Добавляем фичу для сохранения idf
            if feature not in Comments.idf:
                Comments.idf[feature] = idf

            if tf * idf < settings.TF_IDF_EDGE:
                self.features.remove(feature)

            # Если тф-идф ниже границы, убираем ( а так записываем в файл для подсчёта )
            if tf * idf < settings.TF_IDF_EDGE: Comment.tf_idf_words += str(feature) + "\n"

    def load_tf_idf(self):
        for feature in self.features:
            tf = self.cnt[feature] / len(self.text.split(' '))

            idf = Comments.idf[feature]

            if tf * idf < settings.TF_IDF_EDGE:
                self.features.remove(feature)
                Comment.tf_idf_words += str(feature) + "\n"
            
    def count_values(self):
        # print("Counting values")
        for feature in self.features:
            if feature in Comments.delta_tf_idf_frac:
                self.values[feature] = self.cnt[feature] * Comments.delta_tf_idf_frac[feature]
            else:
                if Comments.features_count[feature]['pos'] == 0: Comments.features_count[feature]['pos'] = 0.1
                if Comments.features_count[feature]['neg'] == 0: Comments.features_count[feature]['neg'] = 0.1
                frac = log10((len(Comments.negative_comments) * Comments.features_count[feature]['pos']) / (len(Comments.positive_comments) * Comments.features_count[feature]['neg']))
            
                Comments.delta_tf_idf_frac[feature] = frac
                self.values[feature] = self.cnt[feature] * frac
                
            # Comments.output += "Feature: {}\nself.cnt: {}\tlog10: {}".format(feature, self.cnt[feature], frac)
            

    # TODO: Создать возможность удаления ненужных N-грамм
    def delete_useless(self):
        for key, value in self.tf_idf.items():
            if value < settings.TF_IDF_EDGE:
                print("Deleting feature: '{}' with value {}".format(key, value))
                self.features.remove(key)
    
    def load_delta_tf_idf(self):
        for feature in self.features:
            if feature in Comments.delta_tf_idf_frac:
                self.values[feature] = self.cnt[feature] * Comments.delta_tf_idf_frac[feature]

    def parse_feature(self, feature):
        # Если послали полную хуйню, возвращаем пустоту => там понимаем что убираем всё
        output = feature

        # Первая буква должна быть обязательно либо русская, либо смайлик, остальное не ебёт ( удаляем самму букву (при таргет неймс всё равно повторки уберуться ))
        isChanged = True
        while isChanged:
            if feature == '':
                break
            first_letter = feature[0]
            code = ord(first_letter)
            if (32 <= code < 1031) or (1108 <= code < 9617) or (10244 <= code < 119859):
                # print(feature, "not in range")
                self.features.remove(feature)
                break
            elif '{n}' in feature:
                feature = feature.replace('{n}', '').strip()
                self.features[_] = feature
            elif '.' in feature:
                feature = feature.replace('.', '').strip()
                self.features[_] = feature
            elif ',' in feature:
                feature = feature.replace(',','').strip()
                self.features[_] = feature
            else:
                somethingChanged = False
