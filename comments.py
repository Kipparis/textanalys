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

        scores = cross_val_score(clf, X, y, cv=5, n_jobs=-1)
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
        wt = Watcher(len(self.comments))
        for comm in self.comments:
            wt.display_load(self.comments.index(comm), "making vector")
            comm.make_vector()
            # Подсчитываем кол-во фичей в этом комменте и добавляем в общую кучу
            if count: comm.count()


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
        count = 1

        # Подсчитываем delta tf - idf
        for comm in self.comments:
            wt.display_load(self.comments.index(comm), "counting delta tf-idf")
            comm.count_values

        ut.write_html('data/delta_tf_idf_log.txt', Comments.output)

        # Сохраняем логарифмическое выражение
        with open('data/delta_tf_idf_frac.json', 'w') as file:
            print(Comments.delta_tf_idf_frac)
            json.dump(Comments.delta_tf_idf_frac, file, ensure_ascii=False)
            print("Ended saving file")

        target_names_text = ""
        counter = 0
        for name in Comments.target_names:
            target_names_text += name + "::|::" 
            counter += 1
        ut.write_html("data/target_names.txt", target_names_text)

        print("First element: {}\tLast element: {}".format(Comments.target_names[0], Comments.target_names[-1]))

        print("target name len: {}".format(len(Comments.target_names)))
        print("counter: {}".format(counter))

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
        print("Data is:\n{}".format(Comments.data))
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
        # Создание вектора признаков
        self.features = self.text.split(' ')

        lastWord = ''
        for word in self.text.split(' '):
            if lastWord == '':
                lastWord = word
            else:
                self.features.append(lastWord + " " + word)
                lastWord = word

        # if self.log: print(self.features)

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
        for feature in self.features:
            if Comments.features_count[feature]['pos'] == 0: Comments.features_count[feature]['pos'] = 0.1
            if Comments.features_count[feature]['neg'] == 0: Comments.features_count[feature]['neg'] = 0.1
            self.values[feature] = self.cnt[feature] * log10((len(Comments.negative_comments) * Comments.features_count[feature]['pos']) / (len(Comments.positive_comments) * Comments.features_count[feature]['neg']))
            Comments.output += "Feature: {}\nself.cnt: {}\tlog10: {}".format(feature, self.cnt[feature], log10((len(Comments.negative_comments) * Comments.features_count[feature]['pos']) / (len(Comments.positive_comments) * Comments.features_count[feature]['neg'])))
            
            frac = (len(Comments.negative_comments) * Comments.features_count[feature]['pos']) / (len(Comments.positive_comments) * Comments.features_count[feature]['neg'])
            print("Frac is\t{}".format(frac))
            Comments.delta_tf_idf_frac[feature] = frac

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

# TODO: Посмотреть можно ли убрать предлоги используя tf-idf