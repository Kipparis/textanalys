import utils as ut
import re

classes = ["review_box ", "review_box short", "review_box ", "review_box short"]

regular = r"\Areview_box+\s\Z"

for string in classes:
    if re.match(regular, string):
        print(regular, "matches", string)