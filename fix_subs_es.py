with open ("data/subtitles_frequency_es.txt", "r") as f:
    with open("data/subs_frequency_es.txt", "w") as f2:
        lines = f.readline().split()
        for i in range(0, len(lines), 2):
            f2.write(f"{lines[i+1]} {lines[i]}\n")