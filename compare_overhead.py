if __name__ == "__main__":
    file1 = open("test1.txt", "r")
    file2 = open("test2.txt", "r")

    file1_pitches = []
    file2_pitches = []
    file1_rolls = []
    file2_rolls = []

    for line in file1.readlines():
        data = line.strip().split(",")
        file1_pitches.append(float(data[0]))
        file1_rolls.append(float(data[1]))
    
    for line in file2.readlines():
        data = line.strip().split(",")
        file2_pitches.append(float(data[0]))
        file2_rolls.append(float(data[1]))
    
    file1.close()
    file2.close()

    roll1sum=0
    roll2sum=0
    pitch1sum=0
    pitch2sum=0

    for i in range(100):
        file1_roll = file1_rolls[i]
        file2_roll = file2_rolls[i]
        file1_pitch = file1_pitches[i]
        file2_pitch = file2_pitches[i]
        roll1sum += file1_roll
        roll2sum += file2_roll
        pitch1sum += file1_pitch
        pitch2sum += file2_pitch

    roll_heitto1 = roll1sum/100
    roll_heitto2 = roll2sum / 100
    pitch_heitto1 = pitch1sum/100
    pitch_heitto2 = pitch2sum / 100
    print(f"roll heitto 1: {roll_heitto1} ")
    print(f"roll heitto 2: {roll_heitto2} ")
    print(f"pitch heitto 1: {pitch_heitto1} ")
    print(f"pitch heitto 2: {pitch_heitto2} ")

    


