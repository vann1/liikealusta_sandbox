
sum = 0
with open("overhead.txt", "r") as file:
    for line in file.readlines():
        sum += float(line)
    average = sum / 1000
    print(average)


