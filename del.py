
score = {
    'Alice': 'Алиса',
    'Bob': 'Боб',
    'Eva': 'Ева',
    'Dima': 'Дима',
}

phrase = input('Get phrase: ')

for i in phrase.split(' '):
    if i in score.keys():
        phrase = phrase.replace(i,score[i])

print(phrase)

