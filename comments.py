import csv

# Для более быстрого написания в файл
import utils as ut

from collections import Counter
from math import log10



class Comments:
    log = False

    comments = []
    positive_comments = []
    negative_comments = []


    owned = []
    reviews = []
    grade = []
    ingame_hours = []
    helpful = []
    funny = []

    texts = []

    def __init__(self):
        print("Initing comments")

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

    def parse_data(self):
        # Создаём классы комментариев
        for raw in zip(self.grade, self.owned, self.reviews,
                self.ingame_hours, self.helpful, self.funny, self.texts):
            # Передаём в новый коммент текст и оценку
            comm = Comment(raw[0], raw[-1])
            self.comments.append(comm)
            if raw[0] == "1":
                print("Appended positive")
                Comments.positive_comments.append(comm)
            else:
                print("Appended negative")
                Comments.negative_comments.append(comm)
            
        # Подсчитываем для каждого коммента вектор признаков
        for comm in self.comments:
            comm.make_vector()

        # Подсчитываем для каждого коммента значения слов в тексте
        for comm in self.comments:
            comm.count_values()

        print("#" * 10, "Parsing data", "#" * 10)

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

#######################################


class Comment:
    log = True

    # Содержит оценку, текст, и т.д. и т.п.
    def __init__(self, grade, text):
        self.grade = grade
        self.text = text

        self.features = []
        self.values = []

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
    def count_values(self):
        print("Counting values")
        
        for feature in self.features:
            if self.log:
                print("Feature: ", feature)
                print("Count: ", self.cnt[feature])
                print("Len positive:", len(Comments.positive_comments))
                print("Len negative:", len(Comments.negative_comments))
                print("Positive texts with this", Comments.count_word_in_positive(Comments, feature))
                print("Negative texts with this", Comments.count_word_in_negative(Comments, feature))
            self.values.append(
                self.cnt[feature] * log10((len(Comments.negative_comments) * Comments.count_word_in_positive(Comments, feature)) / (len(Comments.positive_comments) * Comments.count_word_in_negative(Comments, feature)))
            )
        if self.log: print(self.values)


# TODO: Посмотреть можно ли убрать предлоги используя tf-idf