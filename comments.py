import csv

# Для более быстрого написания в файл
import utils as ut


class Comments:
    log = False


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

    def parse_data(self):

        # TODO: Создаём датасеты и проверяем что везде всё поровну

        print("#" * 10, "Parsing data", "#" * 10)