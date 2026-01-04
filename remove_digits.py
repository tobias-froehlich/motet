import datetime

lines = []
with open('vocabulary.txt', 'r') as f:
    for line in f:
        lines.append(line.strip().split('#'))

with open('vocabulary.txt.new', 'w') as f:
    for line in lines:
        f.write(f"{line[0]}#{line[1]}")
        for entry in line[2:]:
            words = entry.split(',')
            newTimeStamp = datetime.datetime.fromisoformat(words[1]).isoformat(timespec='seconds') 
            f.write(f"#{words[0]},{newTimeStamp}")
        f.write('\n')
