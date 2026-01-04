import datetime
import random
import os
import shutil
import sys

vocabularyFilename = 'vocabulary.txt'
unitSize = 25
repetitionTimeInMinutes = [0, 1, 60, 2*60, 24*60, 2*24*60, 7*24*60, 2*7*24*60, 4*7*24*60, 8*7*24*60, 24*7*24*60]

def stats():
    os.system('clear')
    with open(vocabularyFilename, 'r') as f:
        result = []
        for entry in repetitionTimeInMinutes:
            result.append(0)
        for line in f:
            parts = line.strip().split('#')
            correct = 0
            for part in parts[2:]:
                words = part.split(',')
                if words[0] == 'CORRECT':
                    correct += 1
                elif words[0] == 'INCORRECT':
                    correct = 0
            correct = min(correct, len(result) - 1)
            result[correct] += 1
    for correct in range(len(result)):
        print(f"{correct:2.0f} times correct: {result[correct]}")
    print(f"           total: {sum(result)}")

def add():
    os.system('clear')
    text = input('text:\n').strip()
    if text == 'quit':
        return
    translation = input('translation:\n').strip()
    if translation == 'quit':
        return
    if '#' in text or '#' in translation:
        return
    with open(vocabularyFilename, 'a') as f:
        f.write(f"{text}#{translation}\n")


def edit(remove=False):
    inp = input('search for:\n')
    if inp == 'quit':
        return
    matches = []
    with open(vocabularyFilename, 'r') as f:
        lineIndex = 0
        for line in f:
            lineIndex += 1
            parts = line.strip().split('#')
            if inp in parts[0] or inp in parts[1]:
                matches.append({
                    'lineIndex': lineIndex,
                    'text': parts[0],
                    'translation': parts[1],
                    'results': parts[2:],
                })
    if len(matches) > 5:
        os.system('clear')
        print('Too many matches. Try again.')
        edit()
    elif len(matches) == 0:
        os.system('clear')
        print('No matches. Try again.')
        edit()
    else:
        os.system('clear')
        matchIndex = 0
        for match in matches:
            matchIndex += 1
            print(f"{matchIndex}: {match['text']}\n   {match['translation']}\n\n")
        chosenIndex = 0
        while not 1 <= chosenIndex <= len(matches):
            inp = input('choose one:\n')
            if inp == 'quit':
                return
            try:
                chosenIndex = int(inp)
            except:
                chosenIndex = 0
        match = matches[chosenIndex - 1]
        newText = match['text']
        newTranslation = match['translation']
        if not remove:
            inp = input(f"enter new text:\n{match['text']}\n")
            if inp == 'quit':
                return
            if '#' in inp:
                print('Character # is forbidden.')
                return
            if inp != '':
                newText = inp
            inp = input(f"enter new translation:\n{match['translation']}\n")
            if inp == 'quit':
                return
            if '#' in inp:
                print('Character # is forbidden.')
                return
            if inp != '':
                newTranslation = inp
            os.system('clear')
            print(newText)
            print(newTranslation)
        inp = input()
        if inp == 'quit':
            return
        shutil.move(vocabularyFilename, f"{vocabularyFilename}.bak")
        with open(f"{vocabularyFilename}.bak", 'r') as fin:
            with open(vocabularyFilename, 'w') as fout:
                lineIndex = 0
                for line in fin:
                    lineIndex += 1
                    if lineIndex == match['lineIndex']:
                        if not remove:
                            fout.write(f"{'#'.join([newText , newTranslation, *match['results']])}\n")
                    else:
                        fout.write(line)
        

def learn():
    now = datetime.datetime.now()
    
    def isDue(events):
        if len(events) == 0:
            return True
        counter = 0
        for event in events:
            words = event.split(',')
            if words[0] == 'CORRECT':
                counter += 1
            elif words[0] == 'INCORRECT':
                counter = 0
        if counter < len(repetitionTimeInMinutes):
            repetitionTime = repetitionTimeInMinutes[counter]
        else:
            repetitionTime = repetitionTimeInMinutes[-1]
        diff = (now - datetime.datetime.fromisoformat(words[1])).total_seconds() / 60
        return diff > repetitionTime
 
    def readVocabulary():
        result = []
        resultAll = []
        with open(vocabularyFilename, 'r') as f:
            lineIndex = 0
            for line in f:
                lineIndex += 1
                if line != '' and line != '\n':
                    parts = line.strip().split('#')
                    if isDue(parts[2:]):
                        result.append({
                            'lineIndex': lineIndex,
                            'text': parts[0],
                            'translation': parts[1],
                            'exclude': [],
                        })
                    resultAll.append({
                        'lineIndex': lineIndex,
                        'text': parts[0],
                        'translation': parts[1],
                    })
        return (result, resultAll)
    
    (vocabulary, vocabularyOther) = readVocabulary()
    input(len(vocabulary))
    vocabulary = random.sample(vocabulary, min(unitSize, len(vocabulary)))
   
    for voc in vocabulary:
        for vocOther in vocabularyOther:
            if voc['translation'] == vocOther['translation'] and voc['lineIndex'] != vocOther['lineIndex']:
                voc['exclude'].append(vocOther['text'])
 
    for voc in vocabulary:
        os.system('clear')
        print(voc['translation'])
        if len(voc['exclude']) > 0:
            print(f"({', '.join(voc['exclude'])})")
        inp = input()
        if inp == 'quit':
            break
        if inp == voc['text']:
            voc['result'] = ','.join(['CORRECT', datetime.datetime.now().isoformat()])
        else:
            voc['result'] = ','.join(['INCORRECT', datetime.datetime.now().isoformat()])
            correct = False
            inp = ''
            while not correct and inp != 'quit':
                inp = input(voc['text']+'\n')
                if inp == voc['text']:
                    correct = True
    
    
    shutil.move(vocabularyFilename, vocabularyFilename + '.bak')
    
    lineIndexes = []
    for voc in vocabulary:
        if 'result' in voc:
            lineIndexes.append(voc['lineIndex'])
    
    with open(vocabularyFilename + '.bak', 'r') as fin:
        with open(vocabularyFilename, 'w') as fout:
             lineIndex = 0
             for line in fin:
                 lineIndex += 1
                 fout.write(line.strip())
                 if lineIndex in lineIndexes:
                     for voc in vocabulary:
                         if lineIndex == voc['lineIndex']:
                             fout.write(f"#{voc['result']}")
                 fout.write('\n')

if len(sys.argv) == 1:
    learn()
elif sys.argv[1] == 'stats':
    stats()
elif sys.argv[1] == 'add':
    add()
elif sys.argv[1] == 'remove':
    os.system('clear')
    edit(remove=True)
elif sys.argv[1] == 'edit':
    os.system('clear')
    edit()
