import html
import hashlib
import csv
import io
import requests
import re
from deep_translator import GoogleTranslator

TYPE_MAP = {
    'Substantiv': '名词',
    'Verb': '动词',
    'Präposition': '介词',
    'Konjunktion': '连词',
    'Gebundenes Lexem': '粘着语素',
    'Adjektiv': '形容词',
    'Adverb': '副词',
    'Wortverbindung': '词组',
    'Indefinitpronomen': '不定代词',
    'Abkürzung': '缩写',
    'Interjektion': '感叹词',
    'Personalpronomen': '人称代词',
    'Präfix': '前缀',
    'Possessivpronomen': '所有格代词',
    'Temporaladverb': '时间副词',
    'Lokaladverb': '位置副词',
    'Antwortpartikel': '答语词',
    'Modaladverb': '情态副词',
    'Fokuspartikel': '焦点语气词',
    'Gradpartikel': '程度语气词',
    'Reflexivpronomen': '反身代词',
    'Grußformel': '问候语',
    'Pronomen': '代词',
    'Interrogativpronomen': '疑问代词'
}

COLOR_DER = '#3399FF'
COLOR_DIE = '#FF99CC'
COLOR_DAS = '#FFFF33'

COLOR_RED = '#FF6600'

FLAG = 'A1'


def generate_word_csv_line(word_sentence_pair):
    de_word = word_sentence_pair[0]
    word_type = 'word_type'
    de_sentence = word_sentence_pair[1]
    note_id = 'note_id'
    ch_word = 'ch_word'
    ch_sentence = 'ch_sentence'
    ch_note = ''
    # 处理NoteID
    note_id = FLAG + '_' + hashlib.md5(de_word.encode('utf-8')).hexdigest()
    # 处理词性
    word_type = get_word_type(de_word)
    # 处理翻译
    ch_word = get_word_meaning(de_word)
    ch_sentence = get_sentence_translation(de_sentence)
    # 处理额外信息
    # # 名词：加上词性和复数
    if word_type == '名词':
        ch_note = get_word_noun_note(de_word)
        pass
    if word_type == '动词':
        ch_note = get_word_verb_note(de_word)
        pass
    # # 动词：加上过去分词
    res = generate_safe_csv_line(note_id, de_word, word_type, de_sentence, ch_word, ch_sentence, ch_note)
    return res


def generate_safe_csv_line(note_id, de_word, word_type, de_sentence, ch_word, ch_sentence, ch_note):
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='')
    writer.writerow([note_id, de_word, word_type, de_sentence, ch_word, ch_sentence, ch_note])
    return output.getvalue()


def get_word_type(word):
    raw_text = get_word_raw_text(word)
    # print(raw_text)
    if raw_text is None:
        return '-'
    raw_text_array = raw_text.split('\n')
    for line in raw_text_array:
        if '{{Wortart|' in line:
            return TYPE_MAP[line.split('|')[1]]
        pass
    return '-'


def get_word_meaning(word):
    chinese_meaning_map = {}
    english_meaning_map = {}
    raw_text = get_word_raw_text(word)
    # print(raw_text)
    raw_text_array = []
    if raw_text is not None:
        raw_text_array = raw_text.split('\n')
        pass
    current_flag = 0
    for line in raw_text_array:
        # if 'Ü-Tabelle' in line or ('|zh|' in line and '{{zh-tw}}' not in line) or ('|en|' in line and '{{en}}' in line):
        #     print(line)
        #     pass
        if 'Ü-Tabelle' in line:
            if len(line.split('|')) < 2 or re.sub(r'\D', '', line.split('|')[1]) == '':
                current_flag = current_flag + 1
                pass
            else:
                current_flag = int(re.sub(r'\D', '', line.split('|')[1]))
                pass
            if current_flag not in chinese_meaning_map:
                chinese_meaning_map[current_flag] = set()
                english_meaning_map[current_flag] = set()
                pass
            pass
        if '|zh|' in line and '{{zh-tw}}' not in line:
            line = line.replace('{{ugs.|:}}', '').replace('{{L|Hongkong}}:','')
            meaning_array = line.split('}}')
            for i in range(1, len(meaning_array) - 1):
                this_meaning = meaning_array[i].split('|')[2]
                if len(this_meaning) > 0:
                    chinese_meaning_map[current_flag].add(this_meaning)
                    pass
                pass
            pass
        if '|en|' in line and '{{en}}' in line:
            meaning_array = line.split('}}')
            for i in range(1, len(meaning_array) - 1):
                if '|en|' not in meaning_array[i]:
                    continue
                    pass
                this_meaning = meaning_array[i].split('|')[2]
                if len(this_meaning) > 0:
                    english_meaning_map[current_flag].add(this_meaning)
                    pass
                pass
            pass
        pass
    # print(chinese_meaning_map)
    # print(english_meaning_map)
    res = ''
    for i in range(1, min(current_flag + 1, 3)):
        res = res + str(i) + '.'
        if len(chinese_meaning_map[i]) > 0:
            this_chinese_meaning = ''
            for c in chinese_meaning_map[i]:
                this_chinese_meaning = this_chinese_meaning + c + '/'
                pass
            res = res + this_chinese_meaning[:-1]
            pass
        elif len(english_meaning_map[i]) == 0:
            res = res[:-(1 + len(str(i)))]
            continue
            pass
        else:
            this_english_meaning = ''
            for c in english_meaning_map[i]:
                this_english_meaning = this_english_meaning + c + ' / '
                pass
            res = res + this_english_meaning[:-3]
            pass
        res = res + '<br>'
        pass
    # 如果完全没有中文解释，尝试从中文wiki反查
    chinese_flag = False
    for i in range(1, min(current_flag + 1, 3)):
        if len(chinese_meaning_map[i]) > 0:
            chinese_flag = True
            pass
        pass
    english_flag = False
    for i in range(1, min(current_flag + 1, 3)):
        if len(english_meaning_map[i]) > 0:
            english_flag = True
            pass
        pass
    if not chinese_flag and not english_flag:
        return get_sentence_translation(word)
        # meaning_from_zh = get_word_meaning_from_zh(word)
        # if len(meaning_from_zh) > 0:
        #     return meaning_from_zh
        pass
    return res[:-4]


def get_sentence_translation(sentence):
    translator = GoogleTranslator(source='de', target='zh-CN')
    translation = translator.translate(sentence)
    return html.unescape(translation)


def get_word_noun_note(word):
    raw_text = get_word_raw_text(word)
    raw_array_array = raw_text.split('\n')
    res = ''
    for line in raw_array_array:
        # print(line)
        if '|Genus=' in line:
            # print(line)
            this_gender = line.split('=')[1]
            if this_gender == 'f':
                res = '{}<font color=\'{}\'> die {}</font><br>'.format(res, COLOR_DIE, word)
                pass
            elif this_gender == 'm':
                res = '{}<font color=\'{}\'> der {}</font><br>'.format(res, COLOR_DER, word)
                pass
            elif this_gender == 'n':
                res = '{}<font color=\'{}\'> das {}</font><br>'.format(res, COLOR_DAS, word)
                pass
            elif this_gender == '0':
                res = res + '只有复数形式<br>'
                pass
            pass
        if '|Nominativ Plural=' in line:
            # print(line)
            this_plural = line.split('=')[1]
            res = res + this_plural
            pass
        pass
    return res


def get_word_verb_note(word):
    raw_text = get_word_raw_text(word)
    raw_array_array = raw_text.split('\n')
    res = ''
    partizip = ''
    hilfsverb = False
    for line in raw_array_array:
        # print(line)
        if 'Partizip II=' in line:
            # print(line)
            partizip = line.split('=')[1]
            pass
        if '|Hilfsverb=' in line:
            # print(line)
            hilfsverb = 'sein' == line.split('=')[1]
            pass
        pass
    res = ('\"<font color=\'{}\'>sein</font> '.format(COLOR_RED) if hilfsverb else '\"') + partizip + '\"'
    return res


def get_word_raw_text(word):
    url = "https://de.wiktionary.org/w/api.php"
    headers = {"User-Agent": "AnkiGermanBot/1.0 (your_email@example.com) Python-requests/2.x"}
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": word,
        "rvprop": "content",
        "format": "json",
        "rvslots": "main"
    }
    response = requests.get(url, params=params, headers=headers, timeout=10).json()
    # print(response)
    pages = response.get("query", {}).get("pages", {})
    for page_id in pages:
        if page_id == "-1":
            return None
        return pages[page_id]["revisions"][0]["slots"]["main"]["*"]
    return None


def get_word_raw_text_zh(word):
    url = "https://zh.wiktionary.org/w/api.php"
    headers = {"User-Agent": "AnkiGermanBot/1.0 (your_email@example.com) Python-requests/2.x"}
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": word,
        "rvprop": "content",
        "format": "json",
        "rvslots": "main"
    }
    response = requests.get(url, params=params, headers=headers, timeout=10).json()
    # print(response)
    pages = response.get("query", {}).get("pages", {})
    for page_id in pages:
        if page_id == "-1":
            return None
        return pages[page_id]["revisions"][0]["slots"]["main"]["*"]
    return None


def get_word_meaning_from_zh(word):
    raw_text = get_word_raw_text_zh(word)
    raw_array_array = raw_text.split('\n')
    is_deutsch = False
    is_done = False
    res = ''
    for line in raw_array_array:
        print(line)
        if '==德語==' in line or '==德语==' in line:
            is_deutsch = True
            pass
        if is_deutsch and not is_done:
            if '[[' in line:
                meaning_array = line.split('，')
                for ss in meaning_array:
                    this_meaning = ss[ss.index('[[') + 1 + 1:ss.index(']]')]
                    # print(this_meaning)
                    res = res + this_meaning + '、'
                    pass
                # print(meaning_array)
                is_done = True
                pass
            pass
    return res[:-1]


if __name__ == '__main__':
    # print(get_word_type('Tasche'))
    # print(get_word_type('hören'))
    # print(get_word_meaning('Tasche'))
    # print(get_word_meaning('hören'))
    # print(get_word_meaning('essen'))
    # print(get_word_noun_note('Tasche'))
    # print(get_word_noun_note('Januar'))
    # print(get_word_noun_note('Brot'))
    # print(get_word_noun_note('Eltern'))
    # print(get_word_verb_note('essen'))
    # print(get_word_verb_note('fahren'))
    # print(get_word_raw_text_zh('Ferien'))
    # print(get_word_noun_note('Achtung'))
    # print(get_word_meaning('See'))
    # print(get_word_meaning_from_zh('See'))
    print(generate_word_csv_line(('Kühlschrank', 'Haben wir noch Milch? – Ja, im Kühlschrank.')))
    pass
