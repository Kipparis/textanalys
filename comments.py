import csv

import numpy as np
from scipy import sparse

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn import svm
from sklearn.externals import joblib # Для сохранения
# from sklearn.naive_bayes import MultinomialNB

# Для более быстрого написания в файл
import utils as ut

from collections import Counter
from math import log10

from pprint import pprint


# TODO: Как нибудь с помощью видеокарты ускорить подсчёт этих значений

class Comments:
    log = False

    comments = []


    positive_comments = []
    negative_comments = []

    delta_tl_idf_values = []

    target_names = set()
    
    owned = []
    reviews = []
    grade = []
    ingame_hours = []
    helpful = []
    funny = []

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
        y = self.grades

        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=2)
        print("X_train.shape: {}\ty_train.shape: {}\nX_test.shape: {}\ty_test.shape: {}".format(X_train.shape, y_train.shape, X_test.shape, y_test.shape))

        reg = 1.0 # Параметр регуляризации SVM
        kernel = 'poly'
        print("C value is: {}".format(reg))
        clf = svm.SVC(kernel=kernel, degree=6, C=reg, gamma="scale", random_state=2)

        scores = cross_val_score(clf, X, y, cv=10, n_jobs=-1)
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

        # clf = MultinomialNB().fit(X_train_tfidf, twenty_train.target) # наивный байесовский классификатор

        # print("Точность обучения: {}".format(np.mean(y_test == y_pred)))


    def process_data(self):
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

        Comments.grades = np.array(grades)
        np.save("data/grades.npy", Comments.grade)
        
        # Подсчитываем для каждого коммента вектор признаков
        for comm in self.comments:
            comm.make_vector()

        #####################
        # TODO: С помощью tf-idf удалять стоп-слова
        # удалять не сразу, а только после того как подсчитаны все
        # tf-idf для всех комментариев
        #####################
        for comm in self.comments:
            print("Comm {} from {}".format(self.comments.index(comm), len(self.comments)))
            comm.count_tf_idf()
            # pprint(comm.tf_idf)

        # Выводим бесполезные слова
        ut.write_html("data/tf-idf-useless.txt", Comment.tf_idf_words)

        # Удаляем бесполезные униграммы, т.к. биграммы всё равно остаются
        for comm in self.comments:
            print("Comm {} from {}".format(self.comments.index(comm), len(self.comments)))
            comm.delete_useless()

        # Создаём массив таргет_нэймс
        # Подсчитываем кол-во разных слов
        for comm in self.comments:
            for feature in comm.features:
                Comments.target_names.add(feature)

        print("Comments.target_names len:\n{}".format(len(Comments.target_names)))
        Comments.data = np.zeros((len(Comments.comments), len(Comments.target_names)))
        print("Data shape:\n{}".format(Comments.data.shape))

        # Подсчитываем значения фичей внутри каждого коммента
        for comm in self.comments:
            print("Comm {} from {}".format(self.comments.index(comm), len(self.comments)))
            comm.count_values()

        for comm_ind in range(0, len(self.comments)):
            print("Comm {} from {}".format(self.comments.index(comm), len(self.comments)))
            comm = self.comments[comm_ind]
            for key, value in comm.values.items():
                # print("Comment num: {}".format(comm_ind))
                # print("Key: {}\tValue: {}".format(key, value))
                # print("Index in list(self.taget_names): {}".format(list(self.target_names).index(key)))
                # Каждая строчка - комментарий, столбец - ищем индекс в множестве всех фич
                self.data[comm_ind, (list(self.target_names).index(key))] = value
            # # Заполняем по строчке ndarray

        Comments.s_data = sparse.csr_matrix(self.data)
        print(Comments.s_data)

        data_dest = "data/features.npy"
        print("Saving data to file {}".format(data_dest))
        np.save(data_dest, self.data)
        
        sparce_data_dest = "data/s_features.npy"
        np.save(sparce_data_dest, Comments.s_data)

        print("Ended saving")

        print("#" * 10, "Parsing data", "#" * 10)
        
    def load_data_from_file(self):
        Comments.data = np.load('data/features.npy')
        Comments.s_data = np.load('data/s_features.npy')
        Comments.grades = np.load('data/grades.npy')

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
        print("Counting tf-idf")
        for feature in self.features:
            # Для каждой фичи подсчитываем tf-idf
            count_in_text = self.cnt[feature]
            tf = count_in_text / len(self.text)

            idf = log10(len(Comments.comments) / Comments.count_word_in_comments(Comments, feature))
            self.tf_idf[feature] = tf * idf

            # if tf * idf < 0.00025: print("Feature:\t{}\ttf-idf:\t{}".format(feature, tf * idf))
            if tf * idf < 0.00025: Comment.tf_idf_words += str(feature) + "\n"


    def count_values(self):    
        for feature in self.features:
            self.values[feature] = self.cnt[feature] * log10((len(Comments.negative_comments) * Comments.count_word_in_positive(Comments, feature)) / (len(Comments.positive_comments) * Comments.count_word_in_negative(Comments, feature)))

    # TODO: Создать возможность удаления ненужных N-грамм
    def delete_useless(self):
        for key, value in self.tf_idf.items():
            if value < 0.00025:
                print("Deleting feature: '{}' with value {}".format(key, value))
                self.features.remove(key)


# TODO: Посмотреть можно ли убрать предлоги используя tf-idf