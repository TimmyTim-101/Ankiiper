import pdfplumber
import re


def extract_raw(pdf_path):
    thick_clean_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(8, len(pdf.pages)):
            page = pdf.pages[i]
            text = page.extract_text(layout=True)
            for line in text.split('\n'):
                line = line.replace('Alphabetische', ' ').replace('wortliste', ' ').replace('(sich)', '')
                if len(line.strip()) == 0:
                    continue
                    pass
                match = re.search(r'^([a-zA-ZäöüßÄÖÜ\-\s\,\(\)]+?)\s{3,}(.+)$', line)
                if match:
                    line_array = line.split('  ')
                    strip_line_array = []
                    for l in line_array:
                        strip_l = l.strip()
                        if len(strip_l) > 0:
                            strip_line_array.append(strip_l)
                            pass
                        pass
                    this_line_text = ''
                    for l in strip_line_array:
                        this_line_text = this_line_text + l + '$$$'
                        pass
                    thick_clean_lines.append(this_line_text[:-3])
                    pass
                pass
            pass
        pass
    with open('./docs/goethe_a1/A1_SD1_Wortliste_02_raw.txt', 'w') as f:
        for line in thick_clean_lines:
            f.write(line + '\n')
            pass
        pass
    with open('./docs/goethe_a1/A1_SD1_Wortliste_02_manual.txt', 'w') as f:
        for line in thick_clean_lines:
            if line[0].islower() and '$$$' not in line and line[:3] in ['die', 'der', 'das']:
                # 假设是名词，在第二个大写字母前加分隔符
                count = 0
                for i in range(0, len(line)):
                    if line[i].isupper():
                        count += 1
                        pass
                    if count == 2:
                        line = line[:i].strip() + '$$$' + line[i:].strip()
                        break
                        pass
                    pass
                pass
            f.write(('# ' if line[0].islower() and '$$$' not in line else '') + line + ('# ' if line[-1] not in ['.', '?', '!'] and '$$$' in line else '') + '\n')
            pass
        pass
    pass


def extract_precise(txt_path):
    extracted_data = []
    with open(txt_path, 'r') as f:
        for line in f:
            line = line.replace('\n', '').replace('# ', '')
            line_array = line.split('$$$')
            if len(line_array) != 2:
                continue
                pass
            raw_word = line_array[0]
            sentence = line_array[1]
            clean_word = re.sub(r'^(der|die|das)\s+', '', raw_word)
            clean_word = clean_word.split(',')[0].strip()
            extracted_data.append((clean_word, sentence))
            pass
        pass
    with open('./docs/goethe_a1/A1_SD1_Wortliste_02.txt', 'w') as f:
        for line in extracted_data:
            f.write('{}$$${}\n'.format(line[0], line[1]))
            pass
        pass
    pass


if __name__ == '__main__':
    # extract_raw('./docs/goethe_a1/A1_SD1_Wortliste_02.pdf')
    extract_precise('./docs/goethe_a1/A1_SD1_Wortliste_02_manual.txt')
    pass
