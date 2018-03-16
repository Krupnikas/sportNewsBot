import pymorphy2

morph = pymorphy2.MorphAnalyzer()
word = 'понедельник'
parsed_word = morph.parse(word)[0]
print(parsed_word.inflect({'gent'})[0])
