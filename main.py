import os, sys

from comments import Comments

# print("This is the name of the script: ", sys.argv[0])
# print("Number of arguments: ", len(sys.argv))
# print("The arguments are: ", str(sys.argv))

crawl = 0

for arg in sys.argv:
    if arg[0] == "-":
        # Это какая то команда
        if arg[1:] == "crawl":
            print("Scrapy crawl games")
            crawl = 1

# Если параметр crawl был задан, мы сначала всё скрапим 
# И только потом возвращаемся в код
if crawl == 1:
    os.system("scrapy crawl games")
else:
    Comments.load_values(Comments)

print("\n===============\nvvvvvvvvvvvvvvvv\n")
print("Startring processing")
print("\n^^^^^^^^^^^^^^^\n================")