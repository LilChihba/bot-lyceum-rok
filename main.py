import json  # Библиотека для работы с json-файлами
import os  # Библиотека для работы системой
import requests  # Библиотека для отправки http-запросов
import cv2  # Библиотека для обработки изображений
import pytesseract  # Библиотека для распознавания текста на картинке
import mss  # Библиотека для скриншотов
import numpy  # Библиотека для вычислений
import difflib

from PIL import Image, ImageChops
from progress.bar import IncrementalBar  # Библиотека для визуализации прогресса выполнения работы(ProgressBar)
from bs4 import BeautifulSoup  # Библиотека для извлечения данных из файлов html и xml


def create_json():
    download_bar = IncrementalBar('Скачивание вопросов', min=99, index=99, max=100, suffix='%(percent)d%%')

    url = 'https://rokguides.ru/lyceum-of-wisdom/'

    req = requests.get(url)
    result = req.text

    try:
        with open('resources/html.html', 'w', encoding='utf-8') as w_file:
            w_file.write(result)
    except:
        pass

    with open('resources/html.html', 'r', encoding='utf-8') as r_file:
        with download_bar as bar:
            bar.next()
        html = r_file.read()

    soup = BeautifulSoup(html, 'html.parser')
    questions = soup.find_all('td')

    elem1 = ''
    elem2 = ''

    install_bar = IncrementalBar('Установка вопросов', min=2, max=int((len(questions) - 2) / 2))

    try:
        os.remove('resources/questions.json')
    except:
        pass

    for num in range(2, len(questions) - 1):
        if num % 2 == 0:
            elem1 = questions[num].text.replace('\n\t\t\t\t\t\t\t\thttps://rokguides.ru', '').strip()
        elif num % 2 == 1:
            elem2 = questions[num].text.replace('\n\t\t\t\t\t\t\t\thttps://rokguides.ru', '').strip()

        try:
            with open('resources/questions.json') as r_file1:
                file_content = r_file1.read()
                data1 = json.loads(file_content)

            data = {
                elem1: elem2
            }

            data1.update(data)

            with open('resources/questions.json', 'w') as w_file1:
                json.dump(data1, w_file1, indent=4, ensure_ascii=False)

        except:
            data = {
                elem1: elem2
            }

            with open('resources/questions.json', 'w') as w_file2:
                json.dump(data, w_file2, indent=4, ensure_ascii=False)
        finally:
            if num % 2 == 0:
                install_bar.next()
            elif num == len(questions) - 1:
                install_bar.next()

    install_bar.finish()


def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio() * 100


def difference_image(img_old, img_new):
    open_img_old = Image.open(img_old)
    open_img_new = Image.open(img_new)

    result = ImageChops.difference(open_img_old, open_img_new).getbbox()

    return result


def line(quest):
    text = ''
    for i in range(0, len(quest) + 1):
        text += '-'
    return text


def final():
    print("\n\n\nПоздравляем!\n\n")
    cv2.destroyAllWindows()


def bot(select):
    if select == '1':
        monitor = {
            # 845x70
            'top': 360,
            'left': 640,
            'width': 845,
            'height': 70
        }
    elif select == '2':
        monitor = {
            # 850x70
            'top': 405,
            'left': 645,
            'width': 850,
            'height': 70
        }

    screen_win = {
        # 600x90
        'top': 345,
        'left': 655,
        'width': 600,
        'height': 90
    }

    sct = mss.mss()

    pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR\\tesseract.exe'
    os.environ['TESSDATA_PREFIX'] = 'data'

    no_repeat = ''
    counter = 0

    img_old = 'resources/black.png'

    while True:
        img = numpy.asarray(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        save_img_new = Image.fromarray(img)
        save_img_new.save('resources/img_new.png')

        img_win = numpy.asarray(sct.grab(screen_win))
        img_win = cv2.cvtColor(img_win, cv2.COLOR_BGR2RGB)

        # cv2.imshow('test', img)
        # cv2.imshow('test1', img_win)

        text_in_img = str(pytesseract.image_to_string(img, lang='lat+rus+eng', config='--oem 3 --psm 6')).strip()
        text_win = str((pytesseract.image_to_string(img_win, lang='rus', config='--oem 3 --psm 6')).strip())

        with open('resources/questions.json') as r_file:
            data = json.load(r_file)

        if difference_image(img_old, img_new='resources/img_new.png'):
            for quest in data.keys():
                if no_repeat != quest:
                    a = similarity(text_in_img, quest)
                    # a = fuzz.token_set_ratio(text_in_img, quest)
                    if a > 90:
                        start_line = f'╭---------{line(quest)}╮'
                        text1 = f'| Вопрос: {quest} |'
                        text2 = f'| Ответ: {data.get(quest, "не найден 😥")}'
                        end_line = f'╰---------{line(quest)}╯'
                        len_text2 = len(text2)
                        len_line = len(start_line)
                        spaces = len_line - len_text2
                        for n in range(0, spaces):
                            if n == spaces - 1:
                                text2 += '|'
                            else:
                                text2 += ' '
                        print(start_line)
                        print(text1)
                        print(text2)
                        print(end_line)

                        no_repeat = quest
                        counter += 1

                        save_img_old = Image.fromarray(img)
                        save_img_old.save('resources/img_old.png')

                        img_old = 'resources/img_old.png'

                        break

        if cv2.waitKey(25) & 0xFF == ord('q') or text_win == "ПОЗДРАВЛЯЕМ!":
            print("\n\n\nПоздравляем!\n\n")
            cv2.destroyAllWindows()
            break
        # elif select == '1':
        #     if counter == 10:
        #         final()
        #         break
        # elif select == '2':
        #     if counter == 15:
        #         final()
        #         break
        # elif select == '3':
        #     if counter == 20:
        #         final()
        #         break


def main():
    while True:
        select = input('\nВыберите действие: \n'
                       f'[1]. Скачать вопросы. \n'
                       f'[2]. Запустить бота. \n'
                       f'[3]. Выход из программы \n'
                       f'Ваш выбор: ')

        if select == '1':
            create_json()
        elif select == '2':
            select_lyceum = input('\nВыберите тип: \n'
                                  f'[1]. Отборочные испытания \n'
                                  f'[2]. Промежуточный тур \n'
                                  f'[3]. Финальный экзамен \n'
                                  f'[4]. Назад \n'
                                  f'Ваш выбор: ')
            if 1 <= int(select_lyceum) <= 3:
                bot(select_lyceum)
            elif select_lyceum == '4':
                main()
            else:
                print('Введите верное значение!')
        elif select == '3':
            exit()
        else:
            print('Введите верное значение!')


if __name__ == '__main__':
    main()
