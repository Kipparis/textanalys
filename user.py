
class User:
    def __init__(self, game, id, ingameHours, ownedGames, reviews, useful):
        print("Init user")
        self.id = id
        self.hours = ingameHours
        self.games = ownedGames
        self.reviews = reviews
        self.useful = useful
        self.game = game

