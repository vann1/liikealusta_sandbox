if __name__ == "__main__":
    file1 = open("test1.txt", "r")
    file2 = open("test2.txt", "r")

    file1_pitches = []
    file2_pitches = []
    file1_rolls = []
    file2_rolls = []

    for line in file1.readlines():
        data = line.strip().split(",")
        file1_pitches.append(data[0])
        file1_rolls.append(data[1])
    
    for line in file2.readlines():
        data = line.strip().split(",")
        file2_pitches.append(data[0])
        file2_rolls.append(data[1])
    
    file1.close()
    file2.close()

    diffs = []
    diff_sum = 0
    for i in range(100):
        diff = abs(float(file1_pitches[i]) - float(file2_pitches[i]))
        diff_sum += diff
        diffs.append(diff)
    
    avg_diff = diff_sum/len(diffs)
    print(f"avg diff: {avg_diff}")
    


