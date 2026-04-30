import utils

if __name__ == '__main__':
    # word_list = [
    #     ('Bahnhof', 'Ich treffe dich am Bahnhof.'),
    #     ('Tasche', 'Deine Tasche liegt auf dem Tisch.'),
    #     ('Kino', 'Gehen wir heute Abend ins Kino?'),
    #     ('Ferien', 'Wie waren eure Ferien?'),
    #     ('fahren', 'Wir sind mit dem Zug nach Berlin gefahren.'),
    #     ('essen', 'Hast du schon zu Mittag gegessen?'),
    #     ('passieren', 'Was ist gestern Abend passiert?')
    # ]
    word_list = []
    error_word = []
    with open('./docs/goethe_a1/A1_SD1_Wortliste_02.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            line_array = line.split('$$$')
            word = line_array[0]
            sentence = line_array[1]
            word_list.append((word, sentence))
            pass
        pass
    csv_lines = []
    for p in word_list:
        try:
            this_line = utils.generate_word_csv_line(p).replace('\"\"\"', '\"')
            print(this_line)
            csv_lines.append(this_line)
            pass
        except Exception as e:
            print(e)
            print('\033[31m' + str(p) + '\033[0m')
            error_word.append(p)
            pass
        pass
    print('----------------------------------------------')
    print(error_word)
    with open('outputs/A1_SD1_Wortliste_02.csv', 'w') as f:
        for line in csv_lines:
            f.write(line + '\n')
            pass
        pass
    pass
