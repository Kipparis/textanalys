import os, sys

from comments import Comments

# print("This is the name of the script: ", sys.argv[0])
# print("Number of arguments: ", len(sys.argv))
# print("The arguments are: ", str(sys.argv))

crawl = 0
process = 0

for arg in sys.argv:
    if arg[0] == "-":
        command = arg[1:]
        # Это какая то команда
        if command == "crawl":
            print("Scrapy crawl games")
            crawl = 1
        if command == "log":
            Comments.log = True
        if command == "process":
            process = 1

# Если параметр crawl был задан, мы сначала всё скрапим 
# И только потом возвращаемся в код
if crawl == 1:
    os.system("scrapy crawl games")
else:
    Comments.load_values(Comments)

if process == 1:
    # TODO: поменять название функции на process
    Comments.parse_data(Comments)
else:
    Comments.load_data_from_file(Comments)

print("Shape of data is:\n{}".format(Comments.data.shape))

print("\n===============\nvvvvvvvvvvvvvvvv\n")
print("Startring processing")

# Представляем текст в виде вектора признаков
# для каждого текста указываем тональность (уже есть)
# Выбрать алгоритм классификации текста

print("\n^^^^^^^^^^^^^^^\n================")