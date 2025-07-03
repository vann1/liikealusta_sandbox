import random
random.seed(62)
with open("moi2.txt", "a") as f:
    for i in range(100):
        random_roll = round(random.uniform(-16, 16), 2)
        random_pitch = round(random.uniform(-8.5, 8.5), 2)
        f.write(f"{random_pitch}|{random_roll}\n")