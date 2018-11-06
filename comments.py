class Comments:
    count = 0
    owned = []
    reviews = []
    grade = []
    ingame_hours = []
    helpful = []
    funny = []

    texts = []

    def __init__(self):
        print("Initing comments")

    def add_comments(self, text, owned, reviews, 
                    grade, ingame_hours, helpful, funny):
        
        self.count += 1

        self.owned.append(owned)
        self.reviews.append(reviews)
        self.grade.append(grade)
        self.ingame_hours.append(ingame_hours)
        self.helpful.append(helpful)
        self.funny.append(funny)
        self.texts.append(text)

        print('>- Edding comment -<')

    def ouput_values(self):
        print("Comments count:\t{}".format(self.count))

        print("Owned:\n{}".format(self.owned))
        print("Reviews:\n{}".format(self.reviews))
        print("Grade:\n{}".format(self.grade))
        print("Hours:\n{}".format(self.ingame_hours))
        print("Helpful:\n{}".format(self.helpful))
        print("Funny:\n{}".format(self.funny))
        
        # print("Comments:\n{}".format(self.texts))