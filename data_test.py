import csv

with open("cards.csv", "r") as f:
    reader = csv.reader(f)
    next(reader)
    i = 0
    for lines in reader:
        if int(lines[2]) < 6000:
            print(lines)
            i += 1
    print(f"Total cards found: {i}")