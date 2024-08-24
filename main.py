import json
import subprocess
from datetime import datetime, timedelta
import os
import time
import schedule
from collections import Counter

from aiogram import Bot, Dispatcher, executor, types
# from aiogram.dispatcher.filters import Text
# from aiogram.types import ReplyKeyboardRemove, \
#     ReplyKeyboardMarkup, KeyboardButton, \
#     InlineKeyboardMarkup, InlineKeyboardButton
import requests
# import xlrd
# import xlwt
# import openpyxl
# import pandas as pd

from bs4 import BeautifulSoup

import config
import to_exel
import parser_goodscat
import parser_userside
import msg_report
import filtres
from for_api import search_brand

session_goodscat = requests.Session()
session_netup = requests.Session()

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)

answ = ()

url_login_get = "https://us.gblnet.net/"
url_login = "https://us.gblnet.net/body/login"
url = "https://us.gblnet.net/dashboard"

url_login_goodscat = "https://inet.athome.pro/goodscat/user/authorize/"
url_login_netup = "https://billing.athome.pro/"

HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

# Отдельно обработаем сессию Юзера для получения токена
session_users = requests.Session()
req_users = session_users.get(url_login_get)
soup = BeautifulSoup(req_users.content, 'html.parser')
# print(soup)
print("###################")
scripts = soup.find_all('script')
csrf = None
for script in scripts:
    if script.string is not None:
        # print(script.string)
        script_lst = script.string.split(" ")
        # print(script_lst)
        for num, val in enumerate(script_lst):
            if val == "_csrf:":
                csrf = script_lst[num+1]
print(f"csrf {csrf}")


# Глобально создадим обьекты сессий, будем их обновлять перед запуском парсера
if config.vpn_need:
    subprocess.call(['sh', './vpn_up.sh'])
    # Добавим ожидание запуска
    time.sleep(10)
#
data_users = {
    "_csrf": '',
    "return_page": "",
    "username": config.loginUS,
    "password": config.pswUS
}
data_goodscat = {
    "redirect": [1, 1],
    "login": config.login_goodscat,
    "pwd": config.psw_goodscat,
    "auto": "ok",
}
data_netup = {
    "login": config.loginUS,
    "password": config.pswUS,
    "phone": "",
    "redirect": "https://billing.athome.pro/"
}


def create_users_sessions():
    while True:
        try:
            data_users["_csrf"] = csrf[1:-3]
            response_users2 = session_users.post(url_login, data=data_users, headers=HEADERS).text
            # session_users.post(url_login, data=data_users, headers=HEADERS)
            print("Сессия Юзера создана 2")
            print(response_users2)
            return response_users2
        except ConnectionError:
            print("Ошибка создания сессии")
            send_telegram("Ошибка создания сессии UserSide, повтор запроса через 5 минут")
            time.sleep(300)


response_users = create_users_sessions()


# response_users = session_users.post(url_login, data=data_users, headers=HEADERS).text
# print("Сессия Юзера создана 1")


def create_goodscat_sessions():
    while True:
        try:
            response_goodscat2 = session_goodscat.post(url_login_goodscat, data=data_goodscat, headers=HEADERS).text
            # session_users.post(url_login, data=data_users, headers=HEADERS)
            print("Сессия Юзера создана 2")
            return response_goodscat2
        except ConnectionError:
            print("Ошибка создания сессии")
            send_telegram("Ошибка создания сессии Goodscat, повтор запроса через 5 минут")
            time.sleep(300)


# if config.vpn_need:
response_goodscat = create_goodscat_sessions()


# response_goodscat = session_goodscat.post(url_login_goodscat, data=data_goodscat, headers=HEADERS).text
# print("Сессия ГК создана 1")


def create_netup_sessions():
    while True:
        try:
            response_netup2 = session_netup.post(url_login_netup, data=data_netup, headers=HEADERS).text
            # session_users.post(url_login, data=data_users, headers=HEADERS)
            print("Сессия Юзера создана 2")
            return response_netup2
        except ConnectionError:
            print("Ошибка создания сессии")
            send_telegram("Ошибка создания сессии netup, повтор запроса через 5 минут")
            time.sleep(300)


# if config.vpn_need:
response_netup = create_netup_sessions()


# response_netup = session_netup.post(url_login_netup, data=data_netup, headers=HEADERS).text
# print("Сессия Нетаба создана 1")


def create_sessions():
    # Подключимся к vpn
    if config.vpn_need:
        subprocess.call(['sh', './vpn_up.sh'])
        # Добавим ожидание запуска
        time.sleep(10)

    global data_users
    global data_goodscat
    global data_netup

    global session_users
    global session_goodscat
    global session_netup

    # По бесконечному циклу запустим создание сессий
    while True:
        try:
            response_users = session_users.post(url_login, data=data_users, headers=HEADERS).text
            # session_users.post(url_login, data=data_users, headers=HEADERS)
            print("Сессия Юзера создана 2")

            # if config.vpn_need:
            response_goodscat = session_goodscat.post(url_login_goodscat, data=data_goodscat, headers=HEADERS).text
            # session_goodscat.post(url_login_goodscat, data=data_goodscat, headers=HEADERS)
            print("Сессия ГК создана 2")

            # if config.vpn_need:
            response_netup = session_netup.post(url_login_netup, data=data_netup, headers=HEADERS).text
            # session_netup.post(url_login_netup, data=data_netup, headers=HEADERS)
            print("Сессия Нетаба создана 2")
            # print(response_netup)
            break
        except:
            print("Ошибка создания сессии")
            time.sleep(600)


# Тестовая функция для проверки даты
@dp.message_handler(commands=['0'])
async def echo_mess(message: types.Message):
    await bot.send_message(message.chat.id, f"test")


def test_timer():
    print("Таймер работает")
    send_telegram("Бот запущен")
    # Отправим тестовый файл
    send_telegram_file("TOWest/test.txt")


# Функция отправки сообщения в телеграмм
def send_telegram(text_to_bot):
    print(f"Функция отправки сообщения в телеграмм. {text_to_bot}")
    url_msg = f'https://api.telegram.org/bot{config.BOT_API_TOKEN}/sendMessage'
    # Будем отправлять сообщение в чат
    if config.send_to_chat:
        data_to_chat = {
            'chat_id': config.chat_id,
            'text': text_to_bot,
            'parse_mode': 'HTML'
        }
        requests.post(url=url_msg, data=data_to_chat)

    # Будем отправлять сообщение в личку
    if config.send_to_ls:
        data_to_user = {
            'chat_id': config.tg_user_id,
            'text': text_to_bot,
            'parse_mode': 'HTML'
        }
        requests.post(url=url_msg, data=data_to_user)


# Функция отправки файла в телеграмм
def send_telegram_file(file_name):
    print(f"Функция отправки файла в телеграмм.")
    url_file = f'https://api.telegram.org/bot{config.BOT_API_TOKEN}/sendDocument'

    data_for_file = {
        'chat_id': config.chat_id,
        # 'caption': "Отчёт"
    }
    data_for_file_ls = {
        'chat_id': config.tg_user_id,
        # 'caption': "Отчёт"
    }
    # Отправка файла в общий чат
    if config.send_to_chat:
        with open(file_name, 'rb') as f:
            files = {'document': f}
            requests.post(url_file, data=data_for_file, files=files)
            # requests.post(url_file, data=data_for_file_ls, files=files)

    # # Отправка файла в личку
    if config.send_to_ls:
        with open(file_name, 'rb') as f:
            files = {'document': f}
            # requests.post(url_file, data=data_for_file, files=files)
            requests.post(url_file, data=data_for_file_ls, files=files)


# Получить подключенных абонентов за один день
def auto_report():
    # Подключимся к vpn
    if config.vpn_need:
        subprocess.call(['sh', './vpn_up.sh'])
        # Добавим ожидание запуска к vpn
        time.sleep(6)
    # Создадим сессии, подключимся к биллингам. Подключение к впн идет внутри функции
    create_sessions()
    # Запишем предварительно переменные для сохранения даты
    date_user = ""
    date_gk = ""
    name_table = ""
    print("Дата")
    # Получим дату и рассчитаем на -1 день, то есть за "вчера"
    date_now = datetime.now()

    start_day = date_now - timedelta(config.days_ago)  # здесь мы выставляем минус день
    date_now = start_day.strftime("%d.%m.%Y")
    date_user = date_now
    # Для Goodscat нужна дата в обратном формате
    date_gk = start_day.strftime("%Y-%m-%d")
    date_user = start_day.strftime("%d.%m.%Y")
    name_table = f"{date_user}"
    print(start_day)
    print(date_now)
    send_telegram(f"Отчет за {name_table}")

    # Запустим парсеры для ТО Север, по итогу выполнения функции откроем и вышлем файл
    # Вторым аргументом идет вторая дата для периода. Тут же за один день
    if config.day_north:
        day_north(date_user, date_user, date_gk, name_table)
        # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
        try:
            try:
                send_telegram_file(f"TONorth/ТО_Север_{name_table}.xls")
            except:
                print(f"Файл {name_table} не найден")
        except FileNotFoundError:
            send_telegram(f"Файл {name_table} не найден")

    # Ниже для тестов закроем все кроме севера
    # Запустим парсеры для ТО Юг, по итогу выполнения функции откроем и вышлем файл
    # Вторым аргументом идет вторая дата для периода. Тут же за один день
    if config.day_south:
        day_south(date_user, date_user, date_gk, name_table)
        # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
        try:
            try:
                send_telegram_file(f"TOSouth/ТО_Юг_{name_table}.xls")
            except:
                print(f"Файл {name_table} не найден")
        except FileNotFoundError:
            send_telegram(f"Файл {name_table} не найден")

    # Запустим парсеры для ТО Запад, по итогу выполнения функции откроем и вышлем файл
    # Вторым аргументом идет вторая дата для периода. Тут же за один день
    if config.day_west:
        day_west(date_user, date_user, date_gk, name_table)
        # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
        try:
            try:
                send_telegram_file(f"TOWest/ТО_Запад_{name_table}.xls")
            except:
                print(f"Файл {name_table} не найден")
        except FileNotFoundError:
            send_telegram(f"Файл {name_table} не найден")

    # Запустим парсеры для ТО Восток, по итогу выполнения функции откроем и вышлем файл
    # Вторым аргументом идет вторая дата для периода. Тут же за один день
    if config.day_east:
        day_east(date_user, date_user, date_gk, name_table)
        # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
        try:
            try:
                send_telegram_file(f"TOEast/ТО_Восток_{name_table}.xls")
            except:
                print(f"Файл {name_table} не найден")
        except FileNotFoundError:
            send_telegram(f"Файл {name_table} не найден")

    # Отключимся от vpn. Необходимо для удаленного доступа к серверу
    subprocess.call(['sh', './vpn_down.sh'])


# Сохранить адреса в json и вывести по фильтру
def save_connected_houses(answer, t_o, date_now, list_filter):
    new_arr = []
    for i in answer:
        str1 = str(i[3]) + ' ' + str(i[4])
        new_arr.append(str1)
    coll = Counter(new_arr)
    print(f"Тут коллекция: {coll}")
    # Сохраним коллекцию в json
    with open(f'{t_o}/list/{date_now}.json', 'w') as file:
        json.dump(coll, file, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))
    # Временный словарь для сохранения количества заявок
    temp_list = {i: 0 for i in list_filter}
    # Временный словарь для сохранения количества заявок за последний день
    # temp_list_day = {i: 0 for i in list_filter}
    print(f"тут дикт компрешеншон {temp_list}")
    # Стартовые параметры
    # TODO удалить
    with open(f'{t_o}/start_list.json', 'w') as file:
        json.dump(temp_list, file, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))
    # Прочитаем все коллекции в папке
    files = os.listdir(f"{t_o}/list")
    for file in files:
        with open(f'{t_o}/list/{file}', 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            print(f"тут блин data {data}")
            for k, v in data.items():
                # print(f"d {k, v}")
                try:
                    temp_list[k] += v
                    # print(f"k {k} {temp_list[k]}")
                except KeyError:
                    ...
                    # print(f"Ошибка с {k} {v}")

    # Сделаем в виде списка, ибо придется иногда объединять адреса
    list_to_tg = []
    print("Делаем перебор коллекции")
    for v, k in enumerate(list_filter):
        if k[-1] == ":":  # Просто перевод строки
            list_to_tg.append(f"{k}\n")
        # Если в конце скобка, значит нужно объединить несколько адресов
        elif k[-1] == "]":
            # Сложим указанное количество у последних элементов
            # TODO брать 2 последних элемента, нужно будет выделить числа
            num = int(k[-3:-1])
            print(f"Нам нужно взять {num} количество домов. {type(num)}")
            sump = 0
            sump_coll = 0
            for s in range(num):
                sump_coll += coll[list_filter[v-s-1]]
                sump += temp_list[list_filter[v-s-1]]
                print(f"Тут что-то смотрим {list_filter[v-s-1]}")
            # Удалим последние элементы в списке, отдельным циклом, чтобы не сломать
            for s in range(num):
                list_to_tg.pop()
            list_to_tg.append(f"{k[:-4]} - {sump_coll} ({sump})\n")
        # Иначе, если адрес не найден, то 0
        else:
            try:
                list_to_tg.append(f"{k} - {coll[k]} ({temp_list[k]})\n")
            except KeyError:
                list_to_tg.append(f"{k} - 0 ({temp_list[k]})\n")
    text_to_tg = " ".join(list_to_tg)
    send_telegram(text_to_tg)


# Для ТО Запад
# Функция получает дату, запускает парсер циклом, записывает в файл.
# Вызывающая функция читает и отправляет файл боту
def day_west(start_day, date_now, date_for_goodscat, name_table):
    t_o = "TOWest"  # Название для файла
    t_o_link = "TOWest"  # Для ссылки, иногда требуется сделать два запроса
    t_o_link2 = "TOWest2"
    t_o_link3 = "TOWest3"
    t_o_link4 = "TOWest4"
    answer = get_html_users(date_now, start_day, name_table, t_o, t_o_link)
    answer += get_html_users(date_now, start_day, name_table, t_o, t_o_link2)
    answer += get_html_users(date_now, start_day, name_table, t_o, t_o_link3)
    answer += get_html_users(date_now, start_day, name_table, t_o, t_o_link4)
    # print(answer)
    # Добавим парсер Goodscat
    # Список районов, как цикл для перебора и аргумент для ссылки парсеру
    areas = ["Адмиралтейский", "Василеостровский", "Кировский", "Московский",
             "Петроградский", "Фрунзенский", "Центральный"]
    # Два статуса собираем отдельно
    status = ["archive", "tariff"]
    # Запустим парсер меняя статус и район
    # В конфиге есть опция для выключения парсера ГК, ибо с ним долго тестить
    if config.gk_need:
        for st in status:
            for ar in areas:
                time.sleep(config.delay)  # Небольшая задержка от бана
                answer_gk = get_html_goodscat_for_day(date_for_goodscat, ar, t_o, st)
                time.sleep(5)
                answer += answer_gk
                print(answer_gk)
    print(answer)
    to_exel.save_to_exel_from_userside(name_table, answer, t_o)
    # Функционал подсчета адресов
    # "Римского-Корсакова 83-85",
    #                    "Тосина 6к1",
    list_filter = [
                   "Петровский 26к2",
                   "Прилукская 28А",

                   "Волковский 2",
                   "Волковский 4",
                   "Волковский 6",
                   "Волковский 8",
                   "Волковский 10",
                   "Волковский 12",
                   "Волковский 14",
                   "Волковский 16",
                   "Волковский 18",
                   "Волковский 20",
                   "Волковский 22",
                   "Волковский 24",
                   "Волковский 26",
                   "Волковский 28",
                   "Волковский 30",
                   "Волковский(1-я очередь) [15]",

                   "Измайловский 9",
                   "Измайловский 11",
                   "ЖК Галактика (Измайловский) [ 2]",
                   ]
    # save_connected_houses(answer, t_o, date_now, list_filter)
    # new_arr = []
    # for i in answer:
    #     str1 = str(i[3]) + ' ' + str(i[4])
    #     new_arr.append(str1)
    # coll = Counter(new_arr)
    # # Сделаем в виде списка, ибо придется иногда объединять адреса
    # list_to_tg = []
    # print("Делаем перебор коллекции")
    # for i in list_filter:
    #     if i in coll:
    #         list_to_tg.append(f"{i} - {coll[i]} \n")
    #     # Если в конце стоит ":", то это просто текст, его искать не надо
    #     elif i[-1] == ":":
    #         list_to_tg.append(f"{i} \n")
    #     # Если в конце скобка, значит нужно объединить несколько адресов
    #     elif i[-1] == ")":
    #         list_to_tg.append(f"{i} \n")
    #     # Иначе, если адрес не найден, то 0
    #     else:
    #         list_to_tg.append(f"{i} - 0 \n")
    # text_to_tg = " ".join(list_to_tg)


# Для ТО Юг
# Функция получает дату, запускает парсер циклом, записывает в файл.
# Вызывающая функция читает и отправляет файл боту
def day_south(start_day, date_now, date_for_goodscat, name_table):
    t_o = "TOSouth"  # Название для файла
    t_o_link = "TOSouth"  # Для ссылки, иногда требуется сделать два запроса
    t_o_link2 = "TOSouth2"
    answer = get_html_users(date_now, start_day, name_table, t_o, t_o_link)
    answer += get_html_users(date_now, start_day, name_table, t_o, t_o_link2)
    # Добавим парсер Goodscat
    # Список районов, как цикл для перебора и аргумент для ссылки парсеру
    areas = ["Гатчинский",
             "Кировский",
             "Колпино",
             "Красносельский",
             "Ломоносовский",
             "Московский",
             "Фрунзенский",
             "Пушкинский"]
    # Два статуса собираем отдельно
    status = ["archive", "tariff"]
    # Запустим парсер меняя статус и район
    # В конфиге есть опция для выключения парсера ГК, ибо с ним долго тестить
    if config.gk_need:
        for st in status:
            for ar in areas:
                time.sleep(config.delay)  # Небольшая задержка от бана
                answer += get_html_goodscat_for_day(date_for_goodscat, ar, t_o, st)

    to_exel.save_to_exel_from_userside(name_table, answer, t_o)

    list_filter = ["Струве 12",
                   "Московский 183-185/А",
                   ]
    save_connected_houses(answer, t_o, date_now, list_filter)


# Для ТО Север
# Функция получает дату, запускает парсер циклом, записывает в файл.
# Вызывающая функция читает и отправляет файл боту
def day_north(start_day, date_now, date_for_goodscat, name_table):
    answer = []
    t_o = "TONorth"  # Название для файла
    t_o_link = "TONorth"  # Для ссылки, иногда требуется сделать два запроса
    t_o_link2 = "TONorth2"
    # Добавим парсер Goodscat
    # Список районов, как цикл для перебора и аргумент для ссылки парсеру
    areas = ["Академический",
             "Выборгский",
             "Всеволожский",
             "Калининский",
             "Курортный",
             "Пискаревка",
             "Приморский"]
    # Два статуса собираем отдельно
    status = ["archive", "tariff"]
    # Запустим парсер меняя статус и район
    # В конфиге есть опция для выключения парсера ГК, ибо с ним долго тестить
    if config.gk_need:
        for st in status:
            for ar in areas:
                time.sleep(config.delay)  # Небольшая задержка от бана
                answer += get_html_goodscat_for_day(date_for_goodscat, ar, t_o, st)
    # Для севера ЭХ сверху
    answer += get_html_users(date_now, start_day, name_table, t_o, t_o_link)
    answer += get_html_users(date_now, start_day, name_table, t_o, t_o_link2)
    to_exel.save_to_exel_from_userside(name_table, answer, t_o)
    # Функционал подсчета адресов

    list_filter = ["Тихая 13к1",
                   "Тихая 13к1 (ЖК Стороны света): [ 1]",
                   "Просвещения 43",
                   "Просвещения 43 (ЖК Лондон 🇬🇧 парк): [ 1]",
                   "Арсенальная 11",
                   "Арсенальная 11 (ЖК Браун Хаус Фэмили): [ 1]",
                   "Графская 6к3",
                   "Графская 6к3 (ЖК lampo): [ 1]",
                   "Графская 6к4",
                   "Графская 6к4 (ЖК lampo): [ 1]",
                   "Шувалова 30",
                   "Шувалова 30 (ЖК Десяткино 2.0): [ 1]",
                   "Шувалова 32",
                   "Шувалова 32 (ЖК Десяткино 2.0): [ 1]",


                   ]
    """
            Тихая 13к1(ЖК Стороны света) - 0 (0)
        Просвещения 43 (УК Континент-5):  - 1 (5)
        Арсенальная 11 (ЖК Браун Хаус Фэмили):  - 1 (78)
        Графская 6к3(ЖК lampo) - 0 (0)
        Графская 6к4(ЖК lampo) - 0 (8)
        Шувалова 30(ЖК Десяткино 2.0) - 0 (0)
        Шувалова 32(ЖК Десяткино 2.0) - 0 (0)
        """
    save_connected_houses(answer, t_o, date_now, list_filter)
    # list_filter = [
    #                ]
    #
    # save_connected_houses(answer, t_o, date_now, list_filter)
    #
    # new_arr = []
    # for i in answer:
    #     str1 = str(i[3]) + ' ' + str(i[4])
    #     new_arr.append(str1)
    # coll = Counter(new_arr)
    # print(f"Тут коллекция: {coll}")
    # # Сохраним коллекцию в json
    # with open(f'{t_o}/list/{date_now}.json', 'w') as file:
    #     json.dump(coll, file)
    # # Временный словарь для сохранения количества заявок
    # temp_list = {i: 0 for i in list_filter}
    # # Временный словарь для сохранения количества заявок за последний день
    # temp_list_day = {i: 0 for i in list_filter}
    # print(f"тут дикт компрешеншон {temp_list}")
    # # Прочитаем все коллекции в папке
    # files = os.listdir(f"{t_o}/list")
    # for file in files:
    #     with open(f'{t_o}/list/{file}', 'r') as f:
    #         data = json.load(f)
    #         print(f"тут блин data {data}")
    #         for k, v in data.items():
    #             print(f"d {k, v}")
    #             try:
    #                 temp_list[k] += v
    #                 print(f"k {k} {temp_list[k]}")
    #                 # print(f"temp_list[k] {temp_list[k]}")
    #             except KeyError:
    #                 print(f"Ошибка с {k} {v}")
    #
    # # Сделаем в виде списка, ибо придется иногда объединять адреса
    # list_to_tg = []
    # print("Делаем перебор коллекции")
    # for v, k in enumerate(list_filter):
    #     # print(f"key {k}")
    #     # if k in coll:
    #     #     list_to_tg.append(f"{k} - {coll[k]} \n")
    #     # if k in temp_list:
    #     # list_to_tg.append(f"{k} - {temp_list[k]} \n")
    #     # Если в конце стоит ":", то это просто текст, его искать не надо
    #     # elif k[-1] == ":":
    #     if k[-1] == ":":
    #         list_to_tg.append(f"{k} \n")
    #     # Если в конце скобка, значит нужно объединить несколько адресов
    #     elif k[-1] == ")":
    #         # Сложим указанное количество у последних элементов
    #         # TODO брать 2 последних элемента, нужно будет выделить числа
    #         num = int(k[-2])
    #         sump = 0
    #         sump_coll = 0
    #         for s in range(num):
    #             sump_coll += coll[list_filter[v-s-1]]
    #             sump += temp_list[list_filter[v-s-1]]
    #             # print(f"Тут что-то смотрим {list_filter[v-s-1]}")
    #         # Удалим последние элементы в списке, отдельным циклом, чтобы не сломать
    #         for s in range(num):
    #             list_to_tg.pop()
    #         list_to_tg.append(f"{k[:-3]} - {sump_coll} ({sump}) \n")
    #     # Иначе, если адрес не найден, то 0
    #     else:
    #         try:
    #             list_to_tg.append(f"{k} - {coll[k]} ({temp_list[k]}) \n")
    #         except KeyError:
    #             list_to_tg.append(f"{k} - 0 ({temp_list[k]}) \n")
    #         # list_to_tg.append(f"{k} - 0 \n")
    # text_to_tg = " ".join(list_to_tg)
    # send_telegram(text_to_tg)


# Для ТО Восток
# Функция получает дату, запускает парсер циклом, записывает в файл.
# Вызывающая функция читает и отправляет файл боту
def day_east(start_day, date_now, date_for_goodscat, name_table):
    t_o = "TOEast"  # Название для файла
    t_o_link = "TOEast"  # Для ссылки, иногда требуется сделать два запроса
    t_o_link2 = "TOEast2"
    answer = get_html_users(date_now, start_day, name_table, t_o, t_o_link)
    answer += get_html_users(date_now, start_day, name_table, t_o, t_o_link2)
    # Добавим парсер Goodscat
    # Список районов, как цикл для перебора и аргумент для ссылки парсеру
    areas = ["Всеволожский",
             "Красногвардейский",
             "Кудрово",
             "Народный",
             "Невский",
             "Рыбацкое"]
    # Два статуса собираем отдельно
    status = ["archive", "tariff"]
    # Запустим парсер меняя статус и район
    # В конфиге есть опция для выключения парсера ГК, ибо с ним долго тестить
    if config.gk_need:
        for st in status:
            for ar in areas:
                time.sleep(config.delay)  # Небольшая задержка от бана
                answer += get_html_goodscat_for_day(date_for_goodscat, ar, t_o, st)

    to_exel.save_to_exel_from_userside(name_table, answer, t_o)
    # ЖК Цивилизация на Неве(Архивная 9к1, 11к1; Дыбенко 4к1, 6к2: 0(7)
    # Дыбенко 7к(1, 2, 3): 0(22)
    # Дыбенко 8 к(1, 2, 3): 0(14)

    list_filter = [
        "Магнитогорская 5к3",
        "Магнитогорская 5к3 (ЖК Магнифика): [ 1]",
    ]
    save_connected_houses(answer, t_o, date_now, list_filter)


# Недельный отчет
def auto_report_week():
    # Подключимся к vpn
    subprocess.call(['sh', './vpn_up.sh'])
    # Добавим ожидание запуска к vpn
    time.sleep(6)
    # Создадим сессии, подключимся к биллингам
    # create_sessions()
    print("Дата")
    # Соберем прошлую неделю от среды как -10 и -3 дня от текущей даты
    date_now = datetime.now()
    start_week = config.start_week  # 10 Сколько дней назад началась отчетная неделя
    end_week = config.end_week  # 3 Сколько дней назад закончилась отчетная неделя

    # Так же разделим на три отрезка 2, 2 и 3 дня
    # Начало недели
    start_week_day = date_now - timedelta(start_week - 1)  # -1 ибо в цикле ниже, считается до, а не включительно
    start_week_day = start_week_day.strftime("%Y-%m-%d")
    print(start_week_day)

    # Конец первого отрезка недели
    first_end_week_day = date_now - timedelta(start_week - 2)
    first_end_week_day = first_end_week_day.strftime("%Y-%m-%d")
    print(f"{start_week_day} - {first_end_week_day}")

    second_start_week_day = date_now - timedelta(start_week - 3)
    second_start_week_day = second_start_week_day.strftime("%Y-%m-%d")

    # Конец второго отрезка недели
    second_end_week_day = date_now - timedelta(start_week - 4)
    second_end_week_day = second_end_week_day.strftime("%Y-%m-%d")
    print(f"{second_start_week_day} - {second_end_week_day}")

    third_start_week_day = date_now - timedelta(end_week + 2)
    third_start_week_day = third_start_week_day.strftime("%Y-%m-%d")

    # Конец недели
    end_week_day = date_now - timedelta(end_week)
    end_week_day = end_week_day.strftime("%Y-%m-%d")
    print(f"{third_start_week_day} - {end_week_day}")

    name_file_week = f'{start_week_day}-{end_week_day}'
    print(f'Неделя от {start_week_day} до {end_week_day}')

    send_telegram(f"Отчет за {name_file_week}")

    read_report()

    # Запустим парсеры, по итогу выполнения функции откроем и вышлем файлы
    # Вторым аргументом идет вторая дата для периода. Тут же за один день
    if config.week_north:
        week_north(name_file_week, start_week_day, first_end_week_day, second_start_week_day, second_end_week_day,
                   third_start_week_day, end_week_day)
        # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
        try:
            try:
                send_telegram_file(f"TONorth/ТО_Север_{name_file_week}.xls")
            except:
                print(f"Файл {name_file_week} не найден")
        except FileNotFoundError:
            send_telegram(f"Файл {name_file_week} не найден")

    if config.week_south:
        week_south(name_file_week, start_week_day, first_end_week_day, second_start_week_day, second_end_week_day,
                   third_start_week_day, end_week_day)
        # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
        try:
            try:
                send_telegram_file(f"TOSouth/ТО_Юг_{name_file_week}.xls")
            except:
                print(f"Файл {name_file_week} не найден")
        except FileNotFoundError:
            send_telegram(f"Файл {name_file_week} не найден")

    if config.week_west:
        week_west(name_file_week, start_week_day, first_end_week_day, second_start_week_day, second_end_week_day,
                  third_start_week_day, end_week_day)
        # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
        try:
            try:
                send_telegram_file(f"TOWest/ТО_Запад_{name_file_week}.xls")
            except:
                print(f"Файл {name_file_week} не найден")
        except FileNotFoundError:
            send_telegram(f"Файл {name_file_week} не найден")

    if config.week_east:
        week_east(name_file_week, start_week_day, first_end_week_day, second_start_week_day, second_end_week_day,
                  third_start_week_day, end_week_day)
        # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
        try:
            try:
                send_telegram_file(f"TOEast/ТО_Восток_{name_file_week}.xls")
            except:
                print(f"Файл {name_file_week} не найден")
        except FileNotFoundError:
            send_telegram(f"Файл {name_file_week} не найден")

    # Сейчас это прописано отдельно для каждого ТО
    # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
    # try:
    #     try:
    #         # Попробуем прочитать файл и отдельным сообщение выдать результаты
    #         # read_report(name_file_week, "ТО_Запад")
    #         # read_report()
    #         # ...
    #         send_telegram_file(f"TONorth/ТО_Север_{name_file_week}.xls")
    #         send_telegram_file(f"TOSouth/ТО_Юг_{name_file_week}.xls")
    #         send_telegram_file(f"TOWest/ТО_Запад_{name_file_week}.xls")
    #         send_telegram_file(f"TOEast/ТО_Восток_{name_file_week}.xls")
    #     except:
    #         print(f"!!!!!!!!!!! Файл {name_file_week} не найден")
    # except FileNotFoundError:
    #     send_telegram(f"Файл {name_file_week} не найден")

    # Отключимся от vpn. Необходимо для удаленного доступа к серверу
    subprocess.call(['sh', './vpn_down.sh'])


# def read_report(name_table, to):
def read_report(to="ТО_Запад"):
    # book1 = xlrd.open_workbook('TOWest/ТО_Запад_2023-07-01-2023-07-07.xls')
    # book1 = xlwt.Workbook()
    # book1.save()
    # with pd.read_excel('TOWest/ТО_Запад_2023-07-01-2023-07-07.xls') as writer:
    #     print("Читаем книгу с with")
    # wb = openpyxl.load_workbook('TOWest/ТО_Запад_2023-07-01-2023-07-07.xlsm')
    # wb.save()

    # wb = xlrd.load_workbook('TOWest/ТО_Запад_2023-07-01-2023-07-07.xls')
    # writer = pd.ExcelWriter('TOWest/ТО_Запад_2023-07-01-2023-07-07.xlsx', engine='xlsxwriter')
    # writer = pd.ExcelWriter('TOWest/ТО_Запад_2023-07-01-2023-07-07.xlsx')
    #
    # writer.save()

    # Прочитаем таблицу с отчетом
    # book = pd.read_excel(f"TOWest/ТО_Запад_{name_table}.xls")
    # TODO Тут надо еще определить название папки
    # book = pd.read_excel(f"TOWest/ТО_Запад_2023-07-01-2023-07-07.xls")
    # book = pd.read_excel('TOWest/ТО_Запад_2023-07-01-2023-07-07.xlsx')
    # # print()
    #
    # # Интернет
    # # internet = int(book.iloc[2, 2])
    # # internet_refusing = int(book.iloc[1, 6])
    # # internet_another_date = int(book.iloc[2, 6])
    # # internet_in_work_co = int(book.iloc[3, 6])
    # # internet_no_tech = int(book.iloc[5, 6])
    #
    # print(book[1:2])
    # print(book.iloc[2, 2])
    #
    # internet = book.iloc[2, 2]
    # internet_refusing = book.iloc[1, 6]
    # internet_another_date = book.iloc[2, 6]
    # internet_in_work_co = book.iloc[3, 6]
    # internet_no_tech = book.iloc[5, 6]
    # print(f"Интернет: ")
    # print(f"Поступило общее: {internet}")
    # print(f"Отказ: {internet_refusing}")
    # print(f"На другую дату: {internet_another_date}")
    # print(f"В работе КО: {internet_in_work_co}")
    # print(f"НетТехВозм: {internet_no_tech}")

    # ТВ
    # tv = int(book.iloc[16, 2])
    # tv_refusing = int(book.iloc[15, 6])
    # tv_another_date = int(book.iloc[16, 6])
    # tv_in_work_co = int(book.iloc[17, 6])
    # print(f"ТВ: ")
    # print(f"Поступило общее: {tv}")
    # print(f"Отказ: {tv_refusing}")
    # print(f"На другую дату: {tv_another_date}")
    # print(f"В работе КО: {tv_in_work_co}")
    #
    # # Домофон
    # intercom = int(book.iloc[22, 2])
    # intercom_refusing = int(book.iloc[21, 6])
    # intercom_another_date = int(book.iloc[22, 6])
    # intercom_in_work_co = int(book.iloc[23, 6])
    # print(f"Домофон: ")
    # print(f"Поступило общее: {intercom}")
    # print(f"Отказ: {intercom_refusing}")
    # print(f"На другую дату: {intercom_another_date}")
    # print(f"В работе КО: {intercom_in_work_co}")
    #
    # # Сервис интернет
    # serv_internet = int(book.iloc[28, 2])
    # serv_internet_refusing = int(book.iloc[27, 6])
    # serv_internet_another_date = int(book.iloc[28, 6])
    # serv_internet_in_work_co = int(book.iloc[29, 6])
    # print(f"Сервис интернет: ")
    # print(f"Поступило общее: {serv_internet}")
    # print(f"Отказ: {serv_internet_refusing}")
    # print(f"На другую дату: {serv_internet_another_date}")
    # print(f"В работе КО: {serv_internet_in_work_co}")
    #
    # # Сервис ТВ
    # serv_tv = int(book.iloc[34, 2])
    # serv_tv_refusing = int(book.iloc[33, 6])
    # serv_tv_another_date = int(book.iloc[34, 6])
    # serv_tv_in_work_co = int(book.iloc[35, 6])
    # print(f"Сервис ТВ: ")
    # print(f"Поступило "
    #       f"общее: "
    #       f"{serv_tv}")
    # print(f"Отказ: {serv_tv_refusing}")
    # print(f"На другую дату: {serv_tv_another_date}")
    # print(f"В работе КО: {serv_tv_in_work_co}")

    # text_to_bot = f"{to}" \
    #               f"Интернет: " \
    #               f"Поступило общее: {internet} " \
    #               f"Отказ: {internet_refusing} " \
    #               f"На другую дату: {internet_another_date}" \
    #               f"В работе КО: {internet_in_work_co}" \
    #               f"НетТехВозм: {internet_no_tech}"
    #
    # send_telegram(text_to_bot)
    pass


def week_north(name_file_week, start_week_day, first_end_week_day, second_start_week_day,
               second_end_week_day, third_start_week_day, end_week_day):
    t_o = "TONorth"
    t_o_id = 69

    # Список районов, как цикл для перебора и аргумент для ссылки парсеру
    areas = ["Академический",
             "Выборгский",
             "Всеволожский",
             "Калининский",
             "Курортный",
             "Пискаревка",
             "Приморский"]

    # Массив с датами
    week = [f"{start_week_day}+-+{first_end_week_day}",
            f"{second_start_week_day}+-+{second_end_week_day}",
            f"{third_start_week_day}+-+{end_week_day}"]

    # Запустим парсер по группам
    answer_parser_all = [get_html(t_o_id, "internet", start_week_day, end_week_day),
                         get_html(t_o_id, "domofon", start_week_day, end_week_day),
                         get_html(t_o_id, "tv", start_week_day, end_week_day),
                         get_html(t_o_id, "service", start_week_day, end_week_day),
                         get_html(t_o_id, "service_tv", start_week_day, end_week_day)]

    # Запустим парсер сайта, каждый раз меняя дату и район(Дата пока одна неделя, но оставим так)
    # В конфиге есть опция для выключения парсера ГК, ибо с ним долго тестить
    answer_parser = []
    if config.gk_need:
        for area in areas:
            for days in week:
                time.sleep(config.delay)  # Небольшая задержка от бана
                answer_parser += get_html_goodscat(days, area, t_o)  # Запишем в список ответ парсера за один отрезок
    answer_parser_all.append(answer_parser)  # Добавим отрезок в общий список

    if answer_parser_all[0] is None:
        print("Где-то произошла ошибка, отчет пустой")
    else:
        # TODO Отчет сообщение пока не доработан
        # msg = msg_report.calc_msg_report(answer_parser_all)
        #
        # send_telegram(f"ТО Север: {msg}")

        to_exel.save_all_to_exel(name_file_week, answer_parser_all, t_o)


def week_south(name_file_week, start_week_day, first_end_week_day, second_start_week_day,
               second_end_week_day, third_start_week_day, end_week_day):
    t_o = "TOSouth"
    t_o_id = 70

    # Список районов, как цикл для перебора и аргумент для ссылки парсеру

    areas = ["Гатчинский",
             "Кировский",
             "Колпино",
             "Красносельский",
             "Ломоносовский",
             "Московский",
             "Фрунзенский",
             "Пушкинский"]

    # Массив с датами
    week = [f"{start_week_day}+-+{first_end_week_day}",
            f"{second_start_week_day}+-+{second_end_week_day}",
            f"{third_start_week_day}+-+{end_week_day}"]

    # Запустим парсер по группам
    try:
        answer_parser_all = [get_html(t_o_id, "internet", start_week_day, end_week_day) +
                             get_html(72, "internet", start_week_day, end_week_day),
                             get_html(t_o_id, "domofon", start_week_day, end_week_day) +
                             get_html(72, "domofon", start_week_day, end_week_day),
                             get_html(t_o_id, "tv", start_week_day, end_week_day) +
                             get_html(72, "tv", start_week_day, end_week_day),
                             get_html(t_o_id, "service", start_week_day, end_week_day) +
                             get_html(72, "service", start_week_day, end_week_day),
                             get_html(t_o_id, "service_tv", start_week_day, end_week_day) +
                             get_html(72, "service_tv", start_week_day, end_week_day)]
    except TypeError as e:  # Здесь могут складываться пустые ответы
        print(f"ТО Юг, произошла ошибка {e}")
        print("Где-то произошла ошибка, отчет пустой")
        return

    # Запустим парсер сайта, каждый раз меняя дату и район(Дата пока одна неделя, но оставим так)
    # В конфиге есть опция для выключения парсера ГК, ибо с ним долго тестить
    answer_parser = []
    if config.gk_need:
        for area in areas:
            for days in week:
                time.sleep(config.delay)  # Небольшая задержка от бана
                answer_parser += get_html_goodscat(days, area, t_o)  # Запишем в список ответ парсера за один отрезок
    answer_parser_all.append(answer_parser)  # Добавим отрезок в общий список

    if answer_parser_all[0] is None:
        print("Где-то произошла ошибка, отчет пустой")
    else:
        # TODO Отчет сообщение пока не доработан
        # msg = msg_report.calc_msg_report(answer_parser_all)
        #
        # send_telegram(f"ТО Юг: {msg}")

        to_exel.save_all_to_exel(name_file_week, answer_parser_all, t_o)


def week_west(name_file_week, start_week_day, first_end_week_day, second_start_week_day,
              second_end_week_day, third_start_week_day, end_week_day):
    t_o = "TOWest"
    t_o_id = 68

    # Список районов, как цикл для перебора и аргумент для ссылки парсеру
    areas = ["Адмиралтейский", "Василеостровский", "Кировский", "Московский",
             "Петроградский", "Фрунзенский", "Центральный"]

    # Массив с датами
    week = [f"{start_week_day}+-+{first_end_week_day}",
            f"{second_start_week_day}+-+{second_end_week_day}",
            f"{third_start_week_day}+-+{end_week_day}"]

    # Запустим парсер по группам
    answer_parser_all = [get_html(t_o_id, "internet", start_week_day, end_week_day),
                         get_html(t_o_id, "domofon", start_week_day, end_week_day),
                         get_html(t_o_id, "tv", start_week_day, end_week_day),
                         get_html(t_o_id, "service", start_week_day, end_week_day),
                         get_html(t_o_id, "service_tv", start_week_day, end_week_day)]

    # Запустим парсер сайта, каждый раз меняя дату и район(Дата пока одна неделя, но оставим так)
    # В конфиге есть опция для выключения парсера ГК, ибо с ним долго тестить
    answer_parser = []
    if config.gk_need:
        for area in areas:
            for days in week:
                time.sleep(config.delay)  # Небольшая задержка от бана
                answer_parser += get_html_goodscat(days, area, t_o)  # Запишем в список ответ парсера за один отрезок
    answer_parser_all.append(answer_parser)  # Добавим отрезок в общий список

    if answer_parser_all[0] is None:
        print("Где-то произошла ошибка, отчет пустой")
    else:
        # TODO Отчет сообщение пока не доработан
        # msg = msg_report.calc_msg_report(answer_parser_all)
        #
        # send_telegram(f"ТО Запад: {msg}")

        to_exel.save_all_to_exel(name_file_week, answer_parser_all, t_o)


def week_east(name_file_week, start_week_day, first_end_week_day, second_start_week_day,
              second_end_week_day, third_start_week_day, end_week_day):
    t_o = "TOEast"
    t_o_id = 67

    # Список районов, как цикл для перебора и аргумент для ссылки парсеру
    areas = ["Красногвардейский",
             # "Всеволожский",  # Это для ЭтХоума, для Востока там нет ничего
             "Кудрово",
             "Народный",
             "Невский",
             "Рыбацкое"]

    # Массив с датами
    week = [f"{start_week_day}+-+{first_end_week_day}",
            f"{second_start_week_day}+-+{second_end_week_day}",
            f"{third_start_week_day}+-+{end_week_day}"]

    # Запустим парсер по группам
    answer_parser_all = [get_html(t_o_id, "internet", start_week_day, end_week_day),
                         get_html(t_o_id, "domofon", start_week_day, end_week_day),
                         get_html(t_o_id, "tv", start_week_day, end_week_day),
                         get_html(t_o_id, "service", start_week_day, end_week_day),
                         get_html(t_o_id, "service_tv", start_week_day, end_week_day)]

    # Запустим парсер сайта, каждый раз меняя дату и район(Дата пока одна неделя, но оставим так)
    # В конфиге есть опция для выключения парсера ГК, ибо с ним долго тестить
    answer_parser = []
    if config.gk_need:
        for area in areas:
            for days in week:
                time.sleep(config.delay)  # Небольшая задержка от бана
                answer_parser += get_html_goodscat(days, area, t_o)  # Запишем в список ответ парсера за один отрезок
    answer_parser_all.append(answer_parser)  # Добавим отрезок в общий список

    if answer_parser_all[0] is None:
        print("Где-то произошла ошибка, отчет пустой")
    else:
        # TODO Отчет сообщение пока не доработан
        # msg = msg_report.calc_msg_report(answer_parser_all)
        #
        # send_telegram(f"ТО Восток: {msg}")

        to_exel.save_all_to_exel(name_file_week, answer_parser_all, t_o)


# Парсер Юзера, за выбранный период.
def get_html_users(date_now, start_day, name_table, t_o, t_o_link):
    if t_o_link == "TOWest":  # Районы 2267 3215 2275 2261  2264 2276 2269
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
                   f"filter_selector0=customer_mark&customer_mark0_value=66&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
                   f"address_unit_selector1%5B%5D=2267&address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=3215&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=2275&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=adr&address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
                   f"address_unit_selector4%5B%5D=2261&address_unit_selector4%5B%5D=0&" \
                   f"filter_selector5=date_add&date_add5_value2=1&" \
                   f"date_add5_date1={start_day}+00%3A00&date_add5_date2={date_now}+23%3A59&filter_group_by="
    elif t_o_link == "TOWest2":
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
                   f"filter_selector0=customer_mark&customer_mark0_value=66&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
                   f"address_unit_selector1%5B%5D=2264&address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=2276&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=2269&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=date_add&date_add4_value2=1&" \
                   f"date_add4_date1={start_day}+00%3A00&date_add4_date2={date_now}+23%3A59&filter_group_by="
    elif t_o_link == "TOWest3":
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
                   f"filter_selector0=customer_mark&customer_mark0_value=63&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
                   f"address_unit_selector1%5B%5D=2267&address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=3215&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=2275&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=adr&address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
                   f"address_unit_selector4%5B%5D=2261&address_unit_selector4%5B%5D=0&" \
                   f"filter_selector5=date_add&date_add5_value2=1&" \
                   f"date_add5_date1={start_day}+00%3A00&date_add5_date2={date_now}+23%3A59&filter_group_by="
    elif t_o_link == "TOWest4":
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
                   f"filter_selector0=customer_mark&customer_mark0_value=63&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
                   f"address_unit_selector1%5B%5D=2264&address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=2276&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=2269&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=date_add&date_add4_value2=1&" \
                   f"date_add4_date1={start_day}+00%3A00&date_add4_date2={date_now}+23%3A59&filter_group_by="

        # Первая моя версия без метки провайдера
        # t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&filter_selector0=adr&" \
        #       f"address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
        #       f"address_unit_selector0%5B%5D=2267&address_unit_selector0%5B%5D=0&filter_selector1=adr&" \
        #       f"address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
        #       f"address_unit_selector1%5B%5D=3215&address_unit_selector1%5B%5D=0&filter_selector2=adr&" \
        #       f"address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
        #       f"address_unit_selector2%5B%5D=2275&address_unit_selector2%5B%5D=0&filter_selector3=adr&" \
        #       f"address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
        #       f"address_unit_selector3%5B%5D=2261&address_unit_selector3%5B%5D=0&filter_selector4=adr&" \
        #       f"address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
        #       f"address_unit_selector4%5B%5D=2264&address_unit_selector4%5B%5D=0&filter_selector5=adr&" \
        #       f"address_unit_selector5%5B%5D=421&address_unit_selector5%5B%5D=426&" \
        #       f"address_unit_selector5%5B%5D=2276&address_unit_selector5%5B%5D=0&filter_selector6=adr&" \
        #       f"address_unit_selector6%5B%5D=421&address_unit_selector6%5B%5D=426&" \
        #       f"address_unit_selector6%5B%5D=2269&address_unit_selector6%5B%5D=0&filter_selector7=date_add&" \
        #       f"date_add7_value2=1&date_add7_date1={start_day}&date_add7_date2={date_now}&filter_group_by="

    elif t_o_link == "TOSouth":
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&filter_selector0=date_add&date_add0_value2=1&" \
                   f"date_add0_date1={start_day}&date_add0_date2={date_now}&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&" \
                   f"address_unit_selector1%5B%5D=426&address_unit_selector1%5B%5D=2267&" \
                   f"address_unit_selector1%5B%5D=0&filter_selector2=adr&" \
                   f"address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=2275&address_unit_selector2%5B%5D=0&filter_selector3=adr&" \
                   f"address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=2264&address_unit_selector3%5B%5D=0&filter_selector4=adr&" \
                   f"address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
                   f"address_unit_selector4%5B%5D=2266&address_unit_selector4%5B%5D=0&filter_group_by="

    elif t_o_link == "TOSouth2":
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&filter_selector0=date_add&date_add0_value2=1&" \
                   f"date_add0_date1={start_day}&date_add0_date2={date_now}&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&" \
                   f"address_unit_selector1%5B%5D=426&address_unit_selector1%5B%5D=3890&" \
                   f"address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&" \
                   f"address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=2234&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&" \
                   f"address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=1944&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=adr&" \
                   f"address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
                   f"address_unit_selector4%5B%5D=2233&address_unit_selector4%5B%5D=0&" \
                   f"filter_selector5=adr&" \
                   f"address_unit_selector5%5B%5D=421&address_unit_selector5%5B%5D=426&" \
                   f"address_unit_selector5%5B%5D=2235&address_unit_selector5%5B%5D=0&" \
                   f"filter_selector6=adr&" \
                   f"address_unit_selector6%5B%5D=421&address_unit_selector6%5B%5D=426&" \
                   f"address_unit_selector6%5B%5D=3364&address_unit_selector6%5B%5D=0&" \
                   f"filter_group_by="
    # http: // us.gblnet.net / oper /?core_section = customer_list & filter_selector0 = date_add & date_add0_value2 = 1 & date_add0_date1 = 18.12
    # .2023 + 00 % 3
    # A00 & date_add0_date2 = 18.12
    # .2023 + 00 % 3
    # A00 & date_add0_value = & filter_selector1 = adr & address_unit_selector1 % 5
    # B % 5
    # D = 421 & address_unit_selector1 % 5
    # B % 5
    # D = 426 & address_unit_selector1 % 5
    # B % 5
    # D = 3890 & address_unit_selector1 % 5
    # B % 5
    # D = 0 & filter_selector2 = adr & address_unit_selector2 % 5
    # B % 5
    # D = 421 & address_unit_selector2 % 5
    # B % 5
    # D = 426 & address_unit_selector2 % 5
    # B % 5
    # D = 2234 & address_unit_selector2 % 5
    # B % 5
    # D = 0 & filter_selector3 = adr & address_unit_selector3 % 5
    # B % 5
    # D = 421 & address_unit_selector3 % 5
    # B % 5
    # D = 426 & address_unit_selector3 % 5
    # B % 5
    # D = 1944 & address_unit_selector3 % 5
    # B % 5
    # D = 0 & filter_selector4 = adr & address_unit_selector4 % 5
    # B % 5
    # D = 421 & address_unit_selector4 % 5
    # B % 5
    # D = 426 & address_unit_selector4 % 5
    # B % 5
    # D = 2233 & address_unit_selector4 % 5
    # B % 5
    # D = 0 & filter_selector5 = adr & address_unit_selector5 % 5
    # B % 5
    # D = 421 & address_unit_selector5 % 5
    # B % 5
    # D = 426 & address_unit_selector5 % 5
    # B % 5
    # D = 2235 & address_unit_selector5 % 5
    # B % 5
    # D = 0 & filter_selector6 = adr & address_unit_selector6 % 5
    # B % 5
    # D = 421 & address_unit_selector6 % 5
    # B % 5
    # D = 426 & address_unit_selector6 % 5
    # B % 5
    # D = 3364 & address_unit_selector6 % 5
    # B % 5
    # D = 0 & filter_group_by =
    # Тут с двумя уточнениями в Выборгском районе, Мурино и Девяткино, а не хватает Бугров
    # elif t_o_link == "TONorth":  # 2262 2232 3229 2274 3277 3253
    #     t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
    #                f"filter_selector0=adr&address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
    #                f"address_unit_selector0%5B%5D=2262&address_unit_selector0%5B%5D=0&" \
    #                f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
    #                f"address_unit_selector1%5B%5D=2232&address_unit_selector1%5B%5D=0&" \
    #                f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
    #                f"address_unit_selector2%5B%5D=3229&address_unit_selector2%5B%5D=0&" \
    #                f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
    #                f"address_unit_selector3%5B%5D=2274&address_unit_selector3%5B%5D=0&" \
    #                f"filter_selector4=adr&address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
    #                f"address_unit_selector4%5B%5D=3277&address_unit_selector4%5B%5D=2252&" \
    #                f"address_unit_selector4%5B%5D=0&" \
    #                f"filter_selector5=adr&address_unit_selector5%5B%5D=421&" \
    #                f"address_unit_selector5%5B%5D=3253&" \
    #                f"address_unit_selector5%5B%5D=3277&address_unit_selector5%5B%5D=10010&" \
    #                f"address_unit_selector5%5B%5D=0&" \
    #                f"filter_selector6=date_add&" \
    #                f"date_add6_value2=1&date_add6_date1={start_day}&date_add6_date2={date_now}&" \
    #                f"filter_selector7=customer_mark&customer_mark7_value=66&" \
    #                f"filter_group_by="
    #
    # elif t_o_link == "TONorth2":  # 2262 2232 3229 2274 3277 3253
    #     t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
    #                f"filter_selector0=adr&address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
    #                f"address_unit_selector0%5B%5D=2262&address_unit_selector0%5B%5D=0&" \
    #                f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
    #                f"address_unit_selector1%5B%5D=2232&address_unit_selector1%5B%5D=0&" \
    #                f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
    #                f"address_unit_selector2%5B%5D=3229&address_unit_selector2%5B%5D=0&" \
    #                f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
    #                f"address_unit_selector3%5B%5D=2274&address_unit_selector3%5B%5D=0&" \
    #                f"filter_selector4=adr&address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
    #                f"address_unit_selector4%5B%5D=3277&address_unit_selector4%5B%5D=2252&" \
    #                f"address_unit_selector4%5B%5D=0&" \
    #                f"filter_selector5=adr&address_unit_selector5%5B%5D=421&" \
    #                f"address_unit_selector5%5B%5D=3253&" \
    #                f"address_unit_selector5%5B%5D=3277&address_unit_selector5%5B%5D=10010&" \
    #                f"address_unit_selector5%5B%5D=0&" \
    #                f"filter_selector6=date_add&" \
    #                f"date_add6_value2=1&date_add6_date1={start_day}&date_add6_date2={date_now}&" \
    #                f"filter_selector7=customer_mark&customer_mark7_value=63&" \
    #                f"filter_group_by="

    elif t_o_link == "TONorth111":  # 2262 2232 3229 2274 3277 3253
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
                   f"filter_selector0=adr&address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
                   f"address_unit_selector0%5B%5D=2262&address_unit_selector0%5B%5D=0&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
                   f"address_unit_selector1%5B%5D=2232&address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=3229&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=2274&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=adr&address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
                   f"address_unit_selector4%5B%5D=3277&address_unit_selector4%5B%5D=2252&" \
                   f"address_unit_selector4%5B%5D=0&" \
                   f"filter_selector5=adr&address_unit_selector5%5B%5D=421&" \
                   f"address_unit_selector5%5B%5D=3253&" \
                   f"address_unit_selector5%5B%5D=3277&address_unit_selector5%5B%5D=10010&" \
                   f"address_unit_selector5%5B%5D=0&" \
                   f"filter_selector6=date_add&" \
                   f"date_add6_value2=1&date_add6_date1={start_day}&date_add6_date2={date_now}&" \
                   f"filter_selector7=customer_mark&customer_mark7_value=66&" \
                   f"filter_group_by="

    elif t_o_link == "TONorth":
        t_o_link = (f"http://us.gblnet.net/oper/?core_section=customer_list&"
                    f"filter_selector0=adr&address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426"
                    f"&address_unit_selector0%5B%5D=2262&address_unit_selector0%5B%5D=0&"
                    f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426"
                    f"&address_unit_selector1%5B%5D=2232&address_unit_selector1%5B%5D=0&"
                    f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426"
                    f"&address_unit_selector2%5B%5D=3229&address_unit_selector2%5B%5D=0&"
                    f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&"
                    f"address_unit_selector3%5B%5D=2274&address_unit_selector3%5B%5D=0&"
                    f"filter_selector4=adr&address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=3253&"
                    f"address_unit_selector4%5B%5D=3277&address_unit_selector4%5B%5D=0&"
                    f"filter_selector6=date_add&date_add6_value2=1&"
                    f"date_add6_date1={start_day}+00%3A00&date_add6_date2={date_now}+00%3A00&"
                    f"date_add6_value=&filter_selector7=customer_mark&customer_mark7_value=66&filter_group_by=")

    elif t_o_link == "TONorth2":
        t_o_link = (f"http://us.gblnet.net/oper/?core_section=customer_list&"
                    f"filter_selector0=adr&address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426"
                    f"&address_unit_selector0%5B%5D=2262&address_unit_selector0%5B%5D=0&"
                    f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426"
                    f"&address_unit_selector1%5B%5D=2232&address_unit_selector1%5B%5D=0&"
                    f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426"
                    f"&address_unit_selector2%5B%5D=3229&address_unit_selector2%5B%5D=0&"
                    f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&"
                    f"address_unit_selector3%5B%5D=2274&address_unit_selector3%5B%5D=0&"
                    f"filter_selector4=adr&address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=3253&"
                    f"address_unit_selector4%5B%5D=3277&address_unit_selector4%5B%5D=0&"
                    f"filter_selector6=date_add&date_add6_value2=1&"
                    f"date_add6_date1={start_day}+00%3A00&date_add6_date2={date_now}+00%3A00&"
                    f"date_add6_value=&filter_selector7=customer_mark&customer_mark7_value=63&filter_group_by=")

    elif t_o_link == "TONorth222":  # 2262 2232 3229 2274 3277 3253
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
                   f"filter_selector0=adr&address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
                   f"address_unit_selector0%5B%5D=2262&address_unit_selector0%5B%5D=0&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
                   f"address_unit_selector1%5B%5D=2232&address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=3229&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=2274&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=adr&address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
                   f"address_unit_selector4%5B%5D=3277&address_unit_selector4%5B%5D=2252&" \
                   f"address_unit_selector4%5B%5D=0&" \
                   f"filter_selector5=adr&address_unit_selector5%5B%5D=421&" \
                   f"address_unit_selector5%5B%5D=3253&" \
                   f"address_unit_selector5%5B%5D=3277&address_unit_selector5%5B%5D=10010&" \
                   f"address_unit_selector5%5B%5D=0&" \
                   f"filter_selector6=date_add&" \
                   f"date_add6_value2=1&date_add6_date1={start_day}&date_add6_date2={date_now}&" \
                   f"filter_selector7=customer_mark&customer_mark7_value=63&" \
                   f"filter_group_by="

    elif t_o_link == "TOEast":  # Районы: 2265 2268 3277
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
                   f"filter_selector0=customer_mark&customer_mark0_value=66&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
                   f"address_unit_selector1%5B%5D=2265&address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=2268&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=3277&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=date_add&date_add4_value2=1&" \
                   f"date_add4_date1={start_day}+00%3A00&date_add4_date2={date_now}+23%3A59&filter_group_by="

        # f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
        # f"address_unit_selector3%5B%5D=3277&address_unit_selector3%5B%5D=0&" \

    elif t_o_link == "TOEast2":  # Районы: 2265 2268 3277
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&" \
                   f"filter_selector0=customer_mark&customer_mark0_value=63&" \
                   f"filter_selector1=adr&address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
                   f"address_unit_selector1%5B%5D=2265&address_unit_selector1%5B%5D=0&" \
                   f"filter_selector2=adr&address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
                   f"address_unit_selector2%5B%5D=2268&address_unit_selector2%5B%5D=0&" \
                   f"filter_selector3=adr&address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
                   f"address_unit_selector3%5B%5D=3277&address_unit_selector3%5B%5D=0&" \
                   f"filter_selector4=date_add&date_add4_value2=1&" \
                   f"date_add4_date1={start_day}+00%3A00&date_add4_date2={date_now}+23%3A59&filter_group_by="
        # Первая моя версия без метки провайдера
        # t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&filter_selector0=adr&" \
        #            f"address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
        #            f"address_unit_selector0%5B%5D=2265&address_unit_selector0%5B%5D=0&filter_selector1=adr&" \
        #            f"address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
        #            f"address_unit_selector1%5B%5D=2268&address_unit_selector1%5B%5D=0&filter_selector2=adr&" \
        #            f"address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=3253&" \
        #            f"address_unit_selector2%5B%5D=3277&address_unit_selector2%5B%5D=3411&" \
        #            f"address_unit_selector2%5B%5D=0&filter_selector3=date_add&date_add3_value2=1&" \
        #            f"date_add3_date1={start_day}&date_add3_date2={date_now}&filter_group_by="

    print("t_o_link 111")
    print(t_o_link)
    try:
        # Добавим токен в заголовок
        HEADERS["_csrf"] = csrf[1:-3]
        html = session_users.get(t_o_link, headers=HEADERS)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
            table = soup.find_all('tr', class_="cursor_pointer")
            try:
                answer = parser_userside.save_from_userside(table, t_o)
                return answer
            except IndexError:
                return []
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        print(f'{t_o} : {e}')


# Парсер ГК для сбора подключений за один(обязательно вчерашний) день
def get_html_goodscat_for_day(date, area, t_o, status):
    url_link = ""  # Ссылка устанавливается в зависимости от выбора района и даты
    if area == "Адмиралтейский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%D6%E5%ED%F2%F0%E0%EB%FC%ED%FB%E9&search_type%5B2%5D=district&query%5B%5D=%C0%E4%EC%E8%F0%E0%EB%F2%E5%E9%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%D6%E5%ED%F2%F0%E0%EB%FC%ED%FB%E9&search_type%5B2%5D=district&query%5B%5D=%C0%E4%EC%E8%F0%E0%EB%F2%E5%E9%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Академический":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%C0%E4%EC%E8%F0%E0%EB%F2%E5%E9%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%C0%EA%E0%E4%E5%EC%E8%F7%E5%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%C0%E4%EC%E8%F0%E0%EB%F2%E5%E9%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%C0%EA%E0%E4%E5%EC%E8%F7%E5%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Всеволожский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%C2%E0%F1%E8%EB%E5%EE%F1%F2%F0%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%C2%F1%E5%E2%EE%EB%EE%E6%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%C2%E0%F1%E8%EB%E5%EE%F1%F2%F0%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%C2%F1%E5%E2%EE%EB%EE%E6%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Выборгский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%C2%F1%E5%E2%EE%EB%EE%E6%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%C2%FB%E1%EE%F0%E3%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%C2%F1%E5%E2%EE%EB%EE%E6%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%C2%FB%E1%EE%F0%E3%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Гатчинский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%C2%FB%E1%EE%F0%E3%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%C3%E0%F2%F7%E8%ED%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%C2%FB%E1%EE%F0%E3%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%C3%E0%F2%F7%E8%ED%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Калининский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%C3%E0%F2%F7%E8%ED%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%E0%EB%E8%ED%E8%ED%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%C3%E0%F2%F7%E8%ED%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%E0%EB%E8%ED%E8%ED%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Колпино":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CA%E0%EB%E8%ED%E8%ED%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%EE%EB%EF%E8%ED%EE&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CA%E0%EB%E8%ED%E8%ED%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%EE%EB%EF%E8%ED%EE&search_type%5B%5D=district"
    elif area == "Красногвардейский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CA%EE%EB%EF%E8%ED%EE&search_type%5B2%5D=district&query%5B%5D=%CA%F0%E0%F1%ED%EE%E3%E2%E0%F0%E4%E5%E9%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CA%EE%EB%EF%E8%ED%EE&search_type%5B2%5D=district&query%5B%5D=%CA%F0%E0%F1%ED%EE%E3%E2%E0%F0%E4%E5%E9%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Красносельский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CA%F0%E0%F1%ED%EE%E3%E2%E0%F0%E4%E5%E9%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%F0%E0%F1%ED%EE%F1%E5%EB%FC%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CA%F0%E0%F1%ED%EE%E3%E2%E0%F0%E4%E5%E9%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%F0%E0%F1%ED%EE%F1%E5%EB%FC%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Кудрово":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CA%F0%E0%F1%ED%EE%F1%E5%EB%FC%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%F3%E4%F0%EE%E2%EE&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CA%F0%E0%F1%ED%EE%F1%E5%EB%FC%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%F3%E4%F0%EE%E2%EE&search_type%5B%5D=district"
    elif area == "Курортный":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CA%F3%E4%F0%EE%E2%EE&search_type%5B2%5D=district&query%5B%5D=%CA%F3%F0%EE%F0%F2%ED%FB%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CA%F3%E4%F0%EE%E2%EE&search_type%5B2%5D=district&query%5B%5D=%CA%F3%F0%EE%F0%F2%ED%FB%E9&search_type%5B%5D=district"
    elif area == "Ломоносовский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CA%F3%F0%EE%F0%F2%ED%FB%E9&search_type%5B2%5D=district&query%5B%5D=%CB%EE%EC%EE%ED%EE%F1%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CA%F3%F0%EE%F0%F2%ED%FB%E9&search_type%5B2%5D=district&query%5B%5D=%CB%EE%EC%EE%ED%EE%F1%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Народный":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CB%EE%EC%EE%ED%EE%F1%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CD%E0%F0%EE%E4%ED%FB%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CB%EE%EC%EE%ED%EE%F1%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CD%E0%F0%EE%E4%ED%FB%E9&search_type%5B%5D=district"
    elif area == "Невский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CD%E0%F0%EE%E4%ED%FB%E9&search_type%5B2%5D=district&query%5B%5D=%CD%E5%E2%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CD%E0%F0%EE%E4%ED%FB%E9&search_type%5B2%5D=district&query%5B%5D=%CD%E5%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Пискаревка":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CD%E5%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CF%E8%F1%EA%E0%F0%E5%E2%EA%E0&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CD%E5%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CF%E8%F1%EA%E0%F0%E5%E2%EA%E0&search_type%5B%5D=district"
    elif area == "Приморский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CF%E8%F1%EA%E0%F0%E5%E2%EA%E0&search_type%5B2%5D=district&query%5B%5D=%CF%F0%E8%EC%EE%F0%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CF%E8%F1%EA%E0%F0%E5%E2%EA%E0&search_type%5B2%5D=district&query%5B%5D=%CF%F0%E8%EC%EE%F0%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Пушкинский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CF%F0%E8%EC%EE%F0%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CF%F3%F8%EA%E8%ED%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CF%F0%E8%EC%EE%F0%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CF%F3%F8%EA%E8%ED%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Рыбацкое":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CF%F3%F8%EA%E8%ED%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%D0%FB%E1%E0%F6%EA%EE%E5&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CF%F3%F8%EA%E8%ED%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%D0%FB%E1%E0%F6%EA%EE%E5&search_type%5B%5D=district"
    elif area == "Василеостровский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%D0%FB%E1%E0%F6%EA%EE%E5&search_type%5B2%5D=district&query%5B%5D=%C2%E0%F1%E8%EB%E5%EE%F1%F2%F0%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%D0%FB%E1%E0%F6%EA%EE%E5&search_type%5B2%5D=district&query%5B%5D=%C2%E0%F1%E8%EB%E5%EE%F1%F2%F0%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Кировский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%C2%E0%F1%E8%EB%E5%EE%F1%F2%F0%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%E8%F0%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%C2%E0%F1%E8%EB%E5%EE%F1%F2%F0%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CA%E8%F0%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Московский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CA%E8%F0%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CC%EE%F1%EA%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CA%E8%F0%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CC%EE%F1%EA%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Петроградский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CC%EE%F1%EA%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CF%E5%F2%F0%EE%E3%F0%E0%E4%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CC%EE%F1%EA%EE%E2%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%CF%E5%F2%F0%EE%E3%F0%E0%E4%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Фрунзенский":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&search_type%5B0%5D=change_status_date&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&query%5B2%5D=%CF%E5%F2%F0%EE%E3%F0%E0%E4%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%D4%F0%F3%ED%E7%E5%ED%F1%EA%E8%E9&search_type%5B%5D=district"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&search_type%5B0%5D=eta&query%5B1%5D=%D2%E0%F0%E8%F4&search_type%5B1%5D=status&query%5B2%5D=%CF%E5%F2%F0%EE%E3%F0%E0%E4%F1%EA%E8%E9&search_type%5B2%5D=district&query%5B%5D=%D4%F0%F3%ED%E7%E5%ED%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Центральный":
        if status == "archive":
            url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?status_extra_id=&" \
                       f"query%5B%5D={date}&search_type%5B%5D=change_status_date&query%5B%5D=%C0%F0%F5%E8%E2&" \
                       f"search_type%5B%5D=status&query%5B%5D=%D6%E5%ED%F2%F0%E0%EB%FC%ED%FB%E9&" \
                       f"search_type%5B%5D=district&query%5B%5D=&search_type%5B%5D=request_id&query%5B%5D=&" \
                       f"search_type%5B%5D=request_id"
        elif status == "tariff":
            url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&" \
                       f"search_type%5B0%5D=eta&query%5B1%5D=%C0%F0%F5%E8%E2&search_type%5B1%5D=status&" \
                       f"query%5B2%5D=%D6%E5%ED%F2%F0%E0%EB%FC%ED%FB%E9&search_type%5B2%5D=district&" \
                       f"query%5B%5D=%D2%E0%F0%E8%F4&search_type%5B%5D=status"
    else:
        print("Район передан некорректно")
        # !!!! Создать функцию записывающую файл или оправляющую ответ с обьяснением ошибки
        return

    print("url_link 111")
    print(url_link)
    try:
        html = session_goodscat.get(url_link)
        answer = ["Ничего нету"]  # Ответ боту
        if html.status_code == 200:
            # Преобразуем кодировку, на сайте фигня нечитаемая
            html.encoding = "windows-1251"
            soup = BeautifulSoup(html.text, 'lxml')
            # zagolovok = soup.h1
            # print(zagolovok)
            # !!!! Там есть класс td_red, зачем и почему непонятно
            table = soup.find_all('tr', class_="td1")
            # Добавим выделенные красным, у них свой класс
            table += soup.find_all('tr', class_="td_red")
            # Для спорных районов нужно отфильтровать улицы
            if t_o == "TOWest" or t_o == "TOSouth":
                if area == "Кировский":  #  or area == "Московский" or area == "Фрунзенский"
                    print("Есть спорные районы")
                    table = parser_goodscat.street_filter(table, t_o)
            # answer = parser_goodscat.save_from_goodscat_for_day(table, status, date, area)
            # Тестово запускаем из главного файла
            answer = save_from_goodscat_for_day(table, status, date, area, t_o)
            return answer
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        link = url_link  # Заглушка ссылки для ошибки
        print(f'{link} : {e}')


# Функция сбора подключений из ГК за прошлый день. Различается по статусу
# Тестово запускаем из главного файла
def save_from_goodscat_for_day(table, status, date2, area, t_o):
    arr = []
    print(f'Всего должно быть абонентов {len(table)}')
    for i in table:
        user = []
        td_class_all = i.find_all('td', class_="")
        # print(f"td_class_all24146: {td_class_all}")
        try:
            date1 = td_class_all[10].text[0:10]
        except IndexError:
            user = ["!!! Внимание, тут потенциально вьебанное подключение по ЭтХоуму, "
                    "проверьте другим ботом и сообщите разработчику.",
                    "", "", "", "", "", "", "", ""]
            continue
        # Первым делом отсеим даты, при статусе Архив
        # Для статуса Архив, должна быть "вчерашняя" дата, то есть получаемая аргументом
        # if status == "archive":
        if date2 != date1:
            continue

        # У адреса другой класс
        address_class = i.find('td', class_="addr")
        # Тут нужно запустить парсер для Нетаба, но хз как его запускать отсюда
        # user.append(td_class_all[1].text)  # 0 = Номер ГК
        gk_num = td_class_all[1].text
        print(f"Запускаем Нетаб, ищем пользователя: {gk_num}")
        try:
            answer = parser_netup(gk_num)
        except IndexError:
            answer = ["Ошибка Нетаба", "Ошибка Нетаба", "Ошибка Нетаба"]
        # Нужно исключить заявки Горохова. Это мастер ИС
        if answer[1].lower() == "ис" or \
                answer[1].lower() == "и с" or \
                answer[1].lower() == "варюшин к.о." or \
                answer[1].lower() == "варюшин к о" or \
                answer[1].lower() == "варюшин к.о" or \
                answer[1].lower() == "варюшин ко" or \
                answer[1].lower() == "варюшин" or \
                answer[1].lower() == "и.с" or \
                answer[1].lower() == "и.с." or \
                answer[1].lower() == "иис" or \
                answer[1].lower() == "и сс" or \
                answer[1].lower() == "ии с" or \
                answer[1].lower() == "исс":
            print(f"answer23451 {answer}")
            continue
        print(f"answer156 {answer}")

        # Новая функция определения бренда, ЭтХоум или Невское
        # new_brand = ""
        print("################################################")
        print("Пытаемся вычислить Бренд")
        print(f"ls: {answer[0]}")
        try:
            print(f"int(answer[0]) {int(answer[0])}")
            new_brand = search_brand(int(answer[0]))
            print(f"new_brand {new_brand}")
        except ValueError:
            print(f"answer[0] {answer[0]}")
            new_brand = search_brand(answer[0])
            print(f"new_brand {new_brand}")
        # else:
        #     new_brand = "нет"
        user.append(new_brand)  # Бренд
        # user.append("ЭтХоум")  # Бренд

        # У даты нужно обрезать время, заменить тире и развернуть
        date1 = date1.split("-")
        date1 = f"{date1[2]}.{date1[1]}.{date1[0]}"
        user.append(date1)  # Дата

        # Договор
        try:
            user.append(int(answer[0]))
        except ValueError:
            user.append(answer[0])

        # Отдельно берем адрес, заодно уберем лишние пробелы по краям
        address = address_class.text.strip()
        address = address.split(",")
        address_street = address[0].strip()
        print("#############################")
        print(f"address {address}")
        # address = str(address)
        # Тут придется вручную отсеивать поселки
        # TODO Внимание, это нужно так же прописать в parser_userside.py
        # if address_street[0] == "Парголово" or \
        #         address_street[0] == " Шушары" or \
        #         address_street[0] == " Новое Девяткино дер." or \
        #         address_street[0] == " пос. Шушары" or \
        #         address_street[0] == " Кудрово" or \
        #         address_street[0] == " Мурино" or \
        #         address_street[0] == " Бугры пос." or \
        #         address_street[0] == " Репино" or \
        #         address_street[0] == " Сестрорецк" or \
        #         address_street[0] == " Янино-1" or \
        #         address_street[0] == " Янин" or \
        #         address[0] == " Песочный" or \
        #         address[0] == " Лисий" or \
        #         address[0] == " Горелово" or \
        #         address[0] == " Коммунар" or \
        #         address[0] == " Колпино" or \
        #         address[0] == "Колпино" or \
        #         address[0] == " Горская" or \
        #         address[0] == " Понтонный" or \
        #         address[0] == " Тельмана" or \
        #         address[0] == " Тельмана пос." or \
        #         address[0] == " Стрельна" or \
        #         address[0] == " пос. Стрельна" or \
        #         address[0] == " Новогорелово пос.":
        # TODO Внимание, это нужно так же прописать в parser_userside.py
        # TODO перенести в отдельный модуль хотя бы списки
        list_villages = ["Парголово", "Шушары", "Новое Девяткино дер.", "пос. Шушары",
                         "Кудрово", "Мурино", "Бугры пос.", "Репино", "Сестрорецк",
                         "Янино-1", "Песочный", "Лисий", "Горелово", "Коммунар",
                         "Колпино", "Горская", "Понтонный", "Тельмана пос.",
                         "пос. Стрельна", "Новогорелово", ]

        list_district = ["Колпинский р-н", "Ломоносовский р-н", "Всеволожский р-н"]

        if address_street in list_villages:
            street = address[1].strip()
        elif address_street in list_district:
            street = address[2].strip()
        else:
            street = address[0].strip()
        # Дальше у улиц уберем лишние слова отдельным модулем для фильтров
        new_street = filtres.cut_street(street)
        user.append(new_street)
        # user.append(street)

        # Адрес. Тут видимо номер дома?
        try:
            user.append(int(address[-2][2:]))
        except ValueError:
            # В случае ошибки там возможно есть * в адресе, ее можно попробовать убрать
            num_dom = address[-2][2:]
            num_dom_list = list(num_dom)
            if "*" in num_dom_list:  # Проверем поиск * в новосозданном списке
                new_num_dom = num_dom[:-1]
                # Урежем до -1 символа, и снова попробуем прообразовать с числу
                try:
                    user.append(int(new_num_dom))
                except ValueError:
                    user.append(new_num_dom)
            else:
                user.append(address[-2][2:])

        # Адрес. А тут видимо номер квартиры?
        # Необходимо убрать подпись "new" у некоторых квартир
        address_kv = (address[-1][4:])
        if len(address_kv) > 3:
            print(f"Подозрение на подпись 'new' у квартиры {address_kv}")
            if address_kv[-3:] == "new":
                print(f"address_kv[-3:] '{address_kv[-3:]}'. Длинна: {len(address_kv)}")
                # Дополнительно там идет пробел. Непонятно только всегда ли
                user.append(int(address_kv[0:-4]))
            else:
                user.append(int(address[-1][4:]))
        else:
            user.append(int(address[-1][4:]))

        # try:
        #     user.append(int(address_kv2))
        # except ValueError:
        #     user.append(address_kv2)

        user.append(answer[1])  # Мастер
        user.append(area)  # Район
        # TODO тестово пропустим Всеволожский район для Востока
        # Кудрово тоже Всеволожский поэтому заранее не могу отключить район
        # if t_o == "TOEast":
        #     if area == "Всеволожский":
        #         continue
        user.append(answer[2])  # Метраж

        arr.append(user)  # Добавим итог в общий массив с адресами
    return arr


# Парсер Нетаба
# Запуск из файла parser_goodscat.py
def parser_netup(gk_num):
    # Пропишем использование глобальных переменных с сессиями
    # global session_netup
    # session_netup = requests.Session()

    url_link = f"https://billing.athome.pro/payments.php?view={gk_num}&source=inet_dev"
    print(f"url_link: {url_link}")
    try:
        html = session_netup.get(url_link)
        if html.status_code == 200:
            # print("Код ответа 200")
            soup = BeautifulSoup(html.text, 'lxml')
            # table1 = soup.find_all('tr', class_="zebra")
            table1 = soup.find_all("form", class_="")
            table2 = table1[2]
            table3 = table2.find_all('td', class_="")
            # Поскольку ячейки могут изменить свое положение после обновления, будем искать вручную
            num_ls = ""
            monter = ""
            cable = ""
            for num, el in enumerate(table3):
                if el.text == "Номер лицевого счёта:":
                    num_ls = table3[num + 1].text
                    print(f"Номер лицевого счёта: {num_ls}")
                    print(f"Номер ячейки {num}")
                if el.text == "Монтажник":
                    monter = table3[num + 1].input['value']
                    print(f"Монтажник: {monter}")
                    print(f"Номер ячейки {num}")
                if el.text == "Метраж кабеля":
                    cable = table3[num + 1].input['value']
                    print(f"Метраж кабеля: {cable}")
                    print(f"Номер ячейки {num}")
                    # Отдельно возьмем метраж и попытаемся его преобразовать к числу
                    try:
                        cable = int(cable)
                    except ValueError:
                        cable = cable
            answer = [num_ls, monter, cable]
            return answer
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        link = url_link  # Заглушка ссылки для ошибки
        print(f'{link} : {e}')


# Функция для отчета из Юзера: неделя, месяц
def get_html(t_o, mission, start_day, end_day):
    # Номера ТО. Запад = 68, Восток = 67, Коплино = 72, Север = 69, Юг = 70
    url3 = ""
    if mission == "internet":
        url3 = f"https://us.gblnet.net/oper/index.php?core_section=task_list&filter_selector0=task_state&" \
               f"task_state0_value=994&filter_selector1=date_add&date_add1_value2=1&" \
               f"date_add1_date1={start_day}&date_add1_date2={end_day}&filter_selector2=task_type&" \
               f"task_type2_value%5B%5D=31&task_type2_value%5B%5D=1&task_type2_value%5B%5D=41&" \
               f"filter_selector3=task_division_w_staff&task_division_w_staff3_value={t_o}"
    elif mission == "domofon":
        url3 = f"https://us.gblnet.net/oper/index.php?core_section=task_list&filter_selector0=task_state&" \
               f"task_state0_value=994&filter_selector1=date_add&date_add1_value2=1&" \
               f"date_add1_date1={start_day}&date_add1_date2={end_day}&filter_selector2=task_type&" \
               f"task_type2_value%5B%5D=17&task_type2_value%5B%5D=32&" \
               f"filter_selector3=task_division_w_staff&task_division_w_staff3_value={t_o}"
    elif mission == "tv":
        url3 = f"https://us.gblnet.net/oper/index.php?core_section=task_list&filter_selector0=task_state&" \
               f"task_state0_value=994&filter_selector1=date_add&date_add1_value2=1&" \
               f"date_add1_date1={start_day}&date_add1_date2={end_day}&filter_selector2=task_type&" \
               f"task_type2_value%5B%5D=30&task_type2_value%5B%5D=11&task_type2_value%5B%5D=51&" \
               f"filter_selector3=task_division_w_staff&task_division_w_staff3_value={t_o}"
    elif mission == "service":
        url3 = f"https://us.gblnet.net/oper/index.php?core_section=task_list&filter_selector0=task_state&" \
               f"task_state0_value=994&filter_selector1=date_add&date_add1_value2=1&" \
               f"date_add1_date1={start_day}&date_add1_date2={end_day}&filter_selector2=task_type&" \
               f"task_type2_value%5B%5D=140&task_type2_value%5B%5D=4&task_type2_value%5B%5D=33&" \
               f"task_type2_value%5B%5D=76&task_type2_value%5B%5D=79&task_type2_value%5B%5D=2&" \
               f"task_type2_value%5B%5D=89&task_type2_value%5B%5D=22&task_type2_value%5B%5D=23&" \
               f"task_type2_value%5B%5D=126&filter_selector3=task_division_w_staff&task_division_w_staff3_value={t_o}"
    elif mission == "service_tv":
        url3 = f"https://us.gblnet.net/oper/index.php?core_section=task_list&filter_selector0=task_state&" \
               f"task_state0_value=994&filter_selector1=date_add&date_add1_value2=1&" \
               f"date_add1_date1={start_day}&date_add1_date2={end_day}&filter_selector2=task_type&" \
               f"task_type2_value%5B%5D=48&task_type2_value%5B%5D=47&task_type2_value%5B%5D=49&" \
               f"task_type2_value%5B%5D=34&task_type2_value%5B%5D=77&task_type2_value%5B%5D=50&" \
               f"task_type2_value%5B%5D=38&task_type2_value%5B%5D=15&filter_selector3=task_division_w_staff&" \
               f"task_division_w_staff3_value={t_o}"
    print("url3_333")
    print(url3)
    try:
        print("Пробуем скачать страницу")
        HEADERS["_csrf"] = csrf[1:-3]
        html = session_users.get(url3, headers=HEADERS)
        # html = session_users.get(url3)
        answer = []  # Ответ боту
        list_repairs_id = []  # Тут храним ИД ремонтов
        print("Проверка ответа")
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
            table = soup.find_all('tr', class_="cursor_pointer")
            # print(table[0])
            print(f"Длинна: {len(table)}")
            for i in table:  # Цикл по списку всей таблицы
                list_a = i.find_all('a')  # Ищем ссылки во всей таблице
                for ii in list_a:  # Цикл по найденным ссылкам
                    if len(ii.text) == 6 or len(ii.text) == 7:  # Ищем похожесть на ид ремонта, он пока из 6 цифр
                        list_repairs_id.append(ii.text)
            # Перебор полученного списка ремонтов
            if len(list_repairs_id) > 0:
                x = 0  # Счетчик индексов новых ремонтов
                # print(f"list_repairs_id432 {list_repairs_id}")
                # print(f"table {table[-1]}")
                for one_repair_id in table:
                    td_class_all = one_repair_id.find_all('td', class_="")
                    # td_class_all = table[x].find_all('td', class_="")
                    # print(td_class_all)
                    td_class_div_center_all = table[x].find_all('td', class_="div_center")

                    data_repair = td_class_div_center_all[1]
                    data_repair_text = data_repair.text
                    address_repair = td_class_all[0]
                    address_repair_text = address_repair.text.strip()
                    status = td_class_all[1].find_all('span', class_="")
                    # print(status)
                    # print(f"Длинна статуса: {len(status)}")
                    status_text = ""
                    if status is None or len(status) == 0:
                        status_text = "пусто"
                    elif len(status) > 2:
                        status_text = status[-1].text
                    else:
                        # print(f"Ищем текст в: {status}")
                        status_text = status[0].text
                    # Разбить статус на массив, чтобы убрать лишнее
                    status_text = status_text.split(":")
                    status_text = status_text[0]
                    # mission_repair = td_class_all[1].b
                    mission_repair_text = td_class_all[1].b.text

                    # Ищем коммент, чтобы отсеивать продажу/аренду при подключении
                    if mission_repair_text == "Прочее задание ФЛ":
                        comment_repair = table[x].find_all('div', class_="div_journal_opis")
                        # Комментария может не быть, поэтому делаем проверку
                        if len(comment_repair) > 0:
                            comment_repair = comment_repair[0].text
                            comment_repair = comment_repair.split(" ")
                            if "при" in comment_repair and "подключении" in comment_repair:
                                status_text = "Аренда/продажа при подключении"
                        # else:  # Если коммента нет создаем пустую строку
                        #     comment_repair = " "
                        # print(f"comment_repair314: {comment_repair}")
                    # print(f"one_repair_id314: {one_repair_id}")

                    one = [data_repair_text, status_text, address_repair_text, mission_repair_text]
                    answer.append(one)

                    x += 1

            answer.reverse()

            return answer
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        link = url3  # Заглушка ссылки для ошибки
        print(f'{link} : {e}')


# Для отчета из ГК: неделя, месяц. date это сразу период в нужном формате
def get_html_goodscat(date, area, t_o):
    url_link = ""  # Ссылка устанавливается в зависимости от выбора района и даты
    if area == "Адмиралтейский":
        url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CA%E8%F0%EE%E2%F1%EA%E8%E9&search_type%5B1%5D=district&" \
                   f"query%5B%5D=%C0%E4%EC%E8%F0%E0%EB%F2%E5%E9%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Академический":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?status_extra_id=&query%5B%5D={date}&" \
                   f"search_type%5B%5D=period&query%5B%5D=%C0%EA%E0%E4%E5%EC%E8%F7%E5%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district&query%5B%5D=&search_type%5B%5D=request_id&query%5B%5D=&" \
                   f"search_type%5B%5D=request_id&query%5B%5D=&search_type%5B%5D=request_id"
    elif area == "Всеволожский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%C0%EA%E0%E4%E5%EC%E8%F7%E5%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%C2%F1%E5%E2%EE%EB%EE%E6%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district"
    elif area == "Выборгский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%C2%F1%E5%E2%EE%EB%EE%E6%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%C2%FB%E1%EE%F0%E3%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district"
    elif area == "Гатчинский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%C2%FB%E1%EE%F0%E3%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%C3%E0%F2%F7%E8%ED%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district"
    elif area == "Калининский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%C3%E0%F2%F7%E8%ED%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CA%E0%EB%E8%ED%E8%ED%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district"
    elif area == "Колпино":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CA%E8%F0%EE%E2%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CA%EE%EB%EF%E8%ED%EE&" \
                   f"search_type%5B%5D=district"
    elif area == "Красногвардейский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CA%EE%EB%EF%E8%ED%EE&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CA%F0%E0%F1%ED%EE%E3%E2%E0%F0%E4%E5%E9%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district"
    elif area == "Красносельский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CA%F0%E0%F1%ED%EE%E3%E2%E0%F0%E4%E5%E9%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CA%F0%E0%F1%ED%EE%F1%E5%EB%FC%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district"
    elif area == "Кудрово":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CA%F0%EE%ED%F8%F2%E0%E4%F2%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CA%F3%E4%F0%EE%E2%EE&search_type%5B%5D=district"
    elif area == "Курортный":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CA%F3%E4%F0%EE%E2%EE&search_type%5B1%5D=district&" \
                   f"query%5B%5D=%CA%F3%F0%EE%F0%F2%ED%FB%E9&search_type%5B%5D=district"
    elif area == "Ломоносовский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CA%F3%F0%EE%F0%F2%ED%FB%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CB%EE%EC%EE%ED%EE%F1%EE%E2%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district"
    elif area == "Народный":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CB%EE%EC%EE%ED%EE%F1%EE%E2%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CD%E0%F0%EE%E4%ED%FB%E9&search_type%5B%5D=district"
    elif area == "Невский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CD%E0%F0%EE%E4%ED%FB%E9&search_type%5B1%5D=district&" \
                   f"query%5B%5D=%CD%E5%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Пискаревка":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CD%E5%E2%F1%EA%E8%E9&search_type%5B1%5D=district&" \
                   f"query%5B%5D=%CF%E8%F1%EA%E0%F0%E5%E2%EA%E0&search_type%5B%5D=district"
    elif area == "Приморский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CF%E8%F1%EA%E0%F0%E5%E2%EA%E0&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CF%F0%E8%EC%EE%F0%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Пушкинский":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CF%F0%E8%EC%EE%F0%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CF%F3%F8%EA%E8%ED%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Рыбацкое":
        url_link = f"https://inet.athome.pro/goodscat/request/viewAll/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CF%F3%F8%EA%E8%ED%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%D0%FB%E1%E0%F6%EA%EE%E5&search_type%5B%5D=district"
    elif area == "Василеостровский":
        url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CF%E5%F2%F0%EE%E3%F0%E0%E4%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&" \
                   f"query%5B%5D=%C2%E0%F1%E8%EB%E5%EE%F1%F2%F0%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Кировский":
        url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%D6%E5%ED%F2%F0%E0%EB%FC%ED%FB%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CA%E8%F0%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Московский":
        url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%C2%E0%F1%E8%EB%E5%EE%F1%F2%F0%EE%E2%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%CC%EE%F1%EA%EE%E2%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Петроградский":
        url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CC%EE%F1%EA%EE%E2%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&" \
                   f"query%5B%5D=%CF%E5%F2%F0%EE%E3%F0%E0%E4%F1%EA%E8%E9&search_type%5B%5D=district"
    elif area == "Фрунзенский":
        url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%CF%E5%F2%F0%EE%E3%F0%E0%E4%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%D4%F0%F3%ED%E7%E5%ED%F1%EA%E8%E9&" \
                   f"search_type%5B%5D=district"
    elif area == "Центральный":
        url_link = f"https://inet.athome.pro/goodscat/request/plainView/?query%5B0%5D={date}&" \
                   f"search_type%5B0%5D=period&query%5B1%5D=%D4%F0%F3%ED%E7%E5%ED%F1%EA%E8%E9&" \
                   f"search_type%5B1%5D=district&query%5B%5D=%D6%E5%ED%F2%F0%E0%EB%FC%ED%FB%E9&" \
                   f"search_type%5B%5D=district"
    else:
        print("Район передан некорректно")
        # !!!! Создать функцию записывающую файл или оправляющую ответ с обьяснением ошибки
        return

    print("url_link 222")
    print(url_link)
    try:
        html = session_goodscat.get(url_link)
        answer = ["Ничего нету"]  # Ответ боту
        if html.status_code == 200:
            # Преобразуем кодировку, на сайте фигня нечитаемая
            html.encoding = "windows-1251"
            soup = BeautifulSoup(html.text, 'lxml')
            zagolovok = soup.h1
            print(zagolovok)
            # !!!! Там есть класс td_red, зачем и почему непонятно
            table = soup.find_all('tr', class_="td1")
            # Добавим выделенные красным, у них свой класс
            table += soup.find_all('tr', class_="td_red")
            # Для спорных районов нужно отфильтровать улицы
            # Пока только для Запада
            if t_o == "TOWest" or t_o == "TOSouth":
                if area == "Кировский" or area == "Московский" or area == "Фрунзенский":
                    print("Есть спорные районы")
                    table = parser_goodscat.street_filter(table, t_o)
            # print(table)
            answer = parser_goodscat.save_from_goodscat(table)
            return answer
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        link = url_link  # Заглушка ссылки для ошибки
        print(f'{link} : {e}')
    except ConnectionError as e:
        link = url_link  # Заглушка ссылки для ошибки
        print(f'{link} : {e}')


# Создадим папки для хранения отчетов, если их нет
def create_folder():
    if not os.path.exists(f"TOEast"):
        os.makedirs(f"TOEast")
    if not os.path.exists(f"TOEast/list"):
        os.makedirs(f"TOEast/list")
    if not os.path.exists(f"TOWest"):
        os.makedirs(f"TOWest")
    if not os.path.exists(f"TOWest/list"):
        os.makedirs(f"TOWest/list")
    if not os.path.exists(f"TONorth"):
        os.makedirs(f"TONorth")
    if not os.path.exists(f"TONorth/list"):
        os.makedirs(f"TONorth/list")
    if not os.path.exists(f"TOSouth"):
        os.makedirs(f"TOSouth")
    if not os.path.exists(f"TOSouth/list"):
        os.makedirs(f"TOSouth/list")


def main():
    # Создадим сессии, подключимся к биллингам
    # Не будем лишний раз этого делать, только непосредственно перед запуском парсера
    # create_sessions()
    # В случае теста сразу запустим создание отчета
    if config.global_test_day:
        auto_report()
    if config.global_test_week:
        auto_report_week()

    # Автоматический запуск парсера по таймеру.
    # Время запуска берется из конфига(строка)
    schedule.every().day.at(config.time_for_start_parser).do(auto_report)
    schedule.every().wednesday.at("06:00").do(auto_report_week)
    while True:
        schedule.run_pending()


if __name__ == '__main__':
    create_folder()  # Создание папок под ТО
    print("Бот запущен")
    # executor.start_polling(dp, skip_updates=True)
    # auto_report()
    main()
