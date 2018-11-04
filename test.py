import utils as ut



with open("text.txt") as file:
    ut.write_html("temp/games/Project_Hospital/Project_Hospital.html", file.read())



