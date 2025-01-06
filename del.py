
score = [
    ('Alice', 100),
    ('Bob', 90),
    ('Eva', 95),
    ('Dima', 85),
]
score.sort(key=lambda x: x[1],reverse=True)
print(score)
