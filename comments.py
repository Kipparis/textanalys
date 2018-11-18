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
# from sklearn.naive_bayes import MultinomialNB

# Для более быстрого написания в файл
import utils as ut
# для того чтобы имортить переменный настроек
import settings

from collections import Counter
from math import log10

from pprint import pprint


# TODO: Как нибудь с помощью видеокарты ускорить подсчёт этих значений

class Comments:
    log = False

    comments = []


    positive_comments = []
    negative_comments = []

    # {"фича": значение}
    delta_tf_idf_values = {}

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

        # X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=2)
        # print("X_train.shape: {}\ty_train.shape: {}\nX_test.shape: {}\ty_test.shape: {}".format(X_train.shape, y_train.shape, X_test.shape, y_test.shape))

        reg = 1.0 # Параметр регуляризации SVM
        kernel = 'poly'
        print("C value is: {}".format(reg))
        clf = svm.SVC(kernel=kernel, degree=6, C=reg, gamma="scale", random_state=2)

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

        # clf = MultinomialNB().fit(X_train_tfidf, twenty_train.target) # наивный байесовский классификатор

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

        Comments.grades = np.array(grades)
        np.save("data/grades.npy", Comments.grade)
        
        # Создаём словарь, где каждой строке соответстует упорядоченная тройка,
        # где первое значение - сколько раз слов встречается во всех комментариях,
        # второе - сколько раз в положительных
        # третье - сколько раз в отрицательных
        # в дальнейшем, можно использовать эти значения просто вычитая единицу из значения

        count = 1
        if ut.path_exists('data/words_count.json'):
            with open('data/words_count.json', 'r') as file:
                print("Loading words_count from json")
                Comments.features_count = json.load(file)
                count = 0

        # Подсчитываем для каждого коммента вектор признаков
        # from utils import Watcher следить за прогрессом
        for comm in self.comments:
            print("Comm {} from {}\tMaking vector".format(self.comments.index(comm), len(self.comments)))
            comm.make_vector()
            # Подсчитываем кол-во фичей в этом комменте и добавляем в общую кучу
            if count: comm.count()

        if not ut.path_exists('data/words_count.json'):
            with open('data/words_count.json', 'w') as file:
                json.dump(Comments.features_count, file)

        #####################
        # TODO: С помощью tf-idf удалять стоп-слова
        # удалять не сразу, а только после того как подсчитаны все
        # tf-idf для всех комментариев
        #####################
        for comm in self.comments:
            print("Comm {} from {}\tCounting tf-idf".format(self.comments.index(comm), len(self.comments)))
            # Считаем и сразу удаляем ненужные слова
            comm.count_tf_idf()
            # pprint(comm.tf_idf)

        
        # Выводим бесполезные слова
        ut.write_html("data/tf-idf-useless.txt", Comment.tf_idf_words)
        print("OUTPUTED DATA/TF-IDF USELESS")

        # # Удаляем бесполезные униграммы, т.к. биграммы всё равно остаются
        # for comm in self.comments:
        #     print("Comm {} from {}\tDeleting useless".format(self.comments.index(comm), len(self.comments)))
        #     comm.delete_useless()

        # Создаём массив таргет_нэймс
        # Подсчитываем кол-во разных слов
        target_names = set()
        for comm in self.comments:
            print("Comm {} from {}\tCreating target names".format(self.comments.index(comm), len(self.comments)))
            for feature in comm.features:
                target_names.add(feature)

        Comments.target_names = sorted(list(target_names))


        target_names_len = len(Comments.target_names)
        # Загружаем чтобы не считать всё заново
        count = 1
        if ut.path_exists('data/target_names_indexes.json'):
            with open('data/target_names_indexes.json', 'r') as file:
                print("Loading target_names_indexes from json")
                Comments.target_names_dict = json.load(file)
                count = 0

        if count:
            j = 0
            # Сделать по индексам, и когда нашли конечный индекс сразу смещаться на него -1
            # Делать без внутреннего цикла, а просто заводить переменную *текущая буква* и когда другая буква не равна ей просто ставить конечный индекс - новое слово
            for j in range(0, len(Comments.target_names)):
                name = Comments.target_names[j]
                if name == '':
                    continue
                print("{} from {}\tCounting target_names indexes".format(Comments.target_names.index(name), target_names_len))
                letter = name[0]
                if letter not in Comments.target_names_dict:
                    # Находим индекс последней вхождения фичи на эту букву.
                    for i in range(Comments.target_names.index(name), len(Comments.target_names)):
                        print("\n {}'s word in target_names\nSearching for letter: {}\nCurrent feature: {}".format(i, letter, Comments.target_names[i]))
                        
                        if Comments.target_names[i][0] != letter:
                            endEnd = i
                            print("Start for {} = {}\tend = {}".format(letter, Comments.target_names.index(name),i))
                            j = i - 1
                            break
                    # К словарю добавляем индекс в котором мы встретили это слово (т.к. списочек отсортированный) и индекс конечного вхождения который мы нашли ранее
                    Comments.target_names_dict[letter] = str(Comments.target_names.index(name)) + ":" + str(endEnd)

        # Сохраняем то что сейчас написали, т.к. процесс мега трудоёмкий
        if not ut.path_exists('data/target_names_indexes.json'):
            with open('data/target_names_indexes.json', 'w') as file:
                json.dump(Comments.target_names_dict, file)
        
        print("Ended saving file")


        # print("Comments.target_names len:\n{}".format(len(Comments.target_names)))
        # # Comments.data = np.zeros((len(Comments.comments), len(Comments.target_names)))
        # # Создаём разряженную матрицу
        # Comments.data = sparse.lil_matrix((len(Comments.comments), len(Comments.target_names)))
        # print("Data shape:\n{}".format(Comments.data.shape))

        # # Загружаем чтобы не считать всё заново
        # count = 1
        # if ut.path_exists('data/delta_tf_idf.json'):
        #     print("Loading delta_tf_idf")
        #     with open('data/delta_tf_idf.json', 'r') as file:
        #         print("Loading target_names_indexes from json")
        #         Comments.delta_tf_idf_values = json.load(file)
        #         for comm in self.comments:
        #             comm.load_delta_tf_idf()
        #         count = 0

        # # Подсчитываем значения фичей внутри каждого коммента
        # if count:
        #     for comm in self.comments:
        #         print("Comm {} from {}\tCounting delta_tf-idf".format(self.comments.index(comm), len(self.comments)))
        #         comm.count_values()


        # # Сохраняем то что сейчас написали, т.к. процесс мега трудоёмкий
        # if not ut.path_exists('data/delta_tf_idf.json'):
        #     with open('data/delta_tf_idf.json', 'w') as file:
        #         json.dump(Comments.delta_tf_idf_values, file)
        #     # Создаю массив длинной в кол-во фичей и там

        # for i in range(0, len(self.comments)):
        #     print("Comm {} from {}\tMaking rows".format(i, len(self.comments)))            
        #     comment = self.comments[i]
        #     row = np.zeros(shape=(1,len(Comments.target_names)))

        #     # Заполняем одну строчку
        #     for feature in comment.features:
        #         row[0, (list(self.target_names).index(feature))] = comment.values[feature]
            
        #     if i == 0:
        #         data_set = row
        #     else:
        #         data_set = np.r_[data_set, row]

        # print("Data_set shape: {}".format(data_set.shape))

        # self.data = data_set


        # for comm_ind in range(0, len(self.comments)):
        #     print("Comm {} from {}\tCreating matrix".format(self.comments.index(comm), len(self.comments)))
        #     comm = self.comments[comm_ind]
        #     for key, value in comm.values.items():
        #         # print("Comment num: {}".format(comm_ind))
        #         # print("Key: {}\tValue: {}".format(key, value))
        #         # print("Index in list(self.taget_names): {}".format(list(self.target_names).index(key)))
        #         # Каждая строчка - комментарий, столбец - ищем индекс в множестве всех фич
        #         self.data[comm_ind, (list(self.target_names).index(key))] = value
        #     # # Заполняем по строчке ndarray

        # Comments.s_data = sparse.csr_matrix(self.data)
        # print(Comments.s_data)

        # data_dest = "data/features.npy"
        # print("Saving data to file {}".format(data_dest))
        # np.save(data_dest, self.data)
        
        # sparce_data_dest = "data/s_features.npy"
        # np.save(sparce_data_dest, Comments.s_data)

        # print("Ended saving features in files:\n{}\n{}".format(data_dest, sparce_data_dest))
        
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
        print("Counting tf-idf")
        for feature in self.features:
            # Для каждой фичи подсчитываем tf-idf
            count_in_text = self.cnt[feature]
            tf = count_in_text / len(self.text)

            # idf = log10(len(Comments.comments) / Comments.count_word_in_comments(Comments, feature))
            idf = log10(len(Comments.comments) / Comments.features_count[feature]['num_all'])
            self.tf_idf[feature] = tf * idf

            if tf * idf < settings.TF_IDF_EDGE:
                self.features.remove(feature)

            # Если тф-идф ниже границы, убираем ( а так записываем в файл для подсчёта )
            if tf * idf < settings.TF_IDF_EDGE: Comment.tf_idf_words += str(feature) + "\n"


    def count_values(self):    
        for feature in self.features:
            if Comments.features_count[feature]['pos'] == 0: Comments.features_count[feature]['pos'] = 0.1
            if Comments.features_count[feature]['neg'] == 0: Comments.features_count[feature]['neg'] = 0.1
            self.values[feature] = self.cnt[feature] * log10((len(Comments.negative_comments) * Comments.features_count[feature]['pos']) / (len(Comments.positive_comments) * Comments.features_count[feature]['neg']))
            if feature not in Comments.delta_tf_idf_values:
                Comments.delta_tf_idf_values[feature] = log10((len(Comments.negative_comments) * Comments.features_count[feature]['pos']) / (len(Comments.positive_comments) * Comments.features_count[feature]['neg']));

    # TODO: Создать возможность удаления ненужных N-грамм
    def delete_useless(self):
        for key, value in self.tf_idf.items():
            if value < settings.TF_IDF_EDGE:
                print("Deleting feature: '{}' with value {}".format(key, value))
                self.features.remove(key)
    
    def load_delta_tf_idf(self):
        print("loading delta tf idf from file")
        for feature in self.features:
            if feature in Comments.delta_tf_idf_values:
                self.values[feature] = self.cnt[feature] * Comments.delta_tf_idf_values[feature]

# TODO: Посмотреть можно ли убрать предлоги используя tf-idf