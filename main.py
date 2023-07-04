import subprocess
from datetime import datetime, timedelta
import os
import time
import schedule

import xlrd
# import time

from aiogram import Bot, Dispatcher, executor, types
# from aiogram.dispatcher.filters import Text
# from aiogram.types import ReplyKeyboardRemove, \
#     ReplyKeyboardMarkup, KeyboardButton, \
#     InlineKeyboardMarkup, InlineKeyboardButton
import requests
# import xlrd
# import xlwt

from bs4 import BeautifulSoup

import config
import to_exel
import parser_goodscat
import parser_userside

session_goodscat = requests.Session()
session_users = requests.Session()
session_netup = requests.Session()

bot = Bot(token=config.BOT_API_TOKEN)
dp = Dispatcher(bot)

answ = ()

# Запустим скрипт включающий vpn перед загрузкой программы
subprocess.call(['sh', './vpn.sh'])
# Добавим ожидание запуска
time.sleep(6)

url_login = "http://us.gblnet.net/oper/"
url_login_goodscat = "https://inet.athome.pro/goodscat/user/authorize/"
url_login_netup = "https://billing.athome.pro/"

HEADERS = {
    "main": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0"
}

data_users = {
    "action": "login",
    "username": config.loginUS,
    "password": config.pswUS
}
response_users = session_users.post(url_login, data=data_users, headers=HEADERS).text

data_goodscat = {
    "redirect": [1, 1],
    "login": config.login_goodscat,
    "pwd": config.psw_goodscat,
    "auto": "ok",
}
response_goodscat = session_goodscat.post(url_login_goodscat, data=data_goodscat, headers=HEADERS).text

data_netup = {
    "login": config.loginUS,
    "password": config.pswUS,
    "phone": "",
    "redirect": "https://billing.athome.pro/"
}
response_netup = session_netup.post(url_login_netup, data=data_netup, headers=HEADERS).text


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
    subprocess.call(['sh', './vpn.sh'])
    # Добавим ожидание запуска к vpn
    time.sleep(6)
    # Запишем предварительно переменные для сохранения даты
    date_user = ""
    date_gk = ""
    name_table = ""
    print("Дата")
    # Получим дату и рассчитаем на -1 день, то есть за "вчера"
    date_now = datetime.now()
    start_day = date_now - timedelta(1)  # здесь мы выставляем минус день
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
    day_north(date_user, date_user, date_gk, name_table)
    # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
    try:
        try:
            send_telegram_file(f"TONorth/ТО_Север_{name_table}.xls")
        except:
            print(f"Файл {name_table} не найден")
    except FileNotFoundError:
        send_telegram(f"Файл {name_table} не найден")

    # Запустим парсеры для ТО Юг, по итогу выполнения функции откроем и вышлем файл
    # Вторым аргументом идет вторая дата для периода. Тут же за один день
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
    day_east(date_user, date_user, date_gk, name_table)
    # Два исключения, при ошибке в названии вылетает второе исключение, которое я пока не могу определить
    try:
        try:
            send_telegram_file(f"TOEast/ТО_Восток_{name_table}.xls")
        except:
            print(f"Файл {name_table} не найден")
    except FileNotFoundError:
        send_telegram(f"Файл {name_table} не найден")


# Для ТО Запад
def day_west(start_day, date_now, date_for_goodscat, name_table):
    t_o = "TOWest"  # Название для файла
    t_o_link = "TOWest"  # Для ссылки, иногда требуется сделать два запроса
    answer = get_html_users(date_now, start_day, name_table, t_o, t_o_link)
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
                answer += answer_gk
                print(answer_gk)
    print(answer)

    to_exel.save_to_exel_from_userside(name_table, answer, t_o)


# Для ТО Юг
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


# Для ТО Север
def day_north(start_day, date_now, date_for_goodscat, name_table):
    answer = []
    t_o = "TONorth"  # Название для файла
    t_o_link = "TONorth"  # Для ссылки, иногда требуется сделать два запроса
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
    to_exel.save_to_exel_from_userside(name_table, answer, t_o)


# Для ТО Восток
def day_east(start_day, date_now, date_for_goodscat, name_table):
    t_o = "TOEast"  # Название для файла
    t_o_link = "TOEast"  # Для ссылки, иногда требуется сделать два запроса
    answer = get_html_users(date_now, start_day, name_table, t_o, t_o_link)
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


# Парсер Юзера, за выбранный период.
def get_html_users(date_now, start_day, name_table, t_o, t_o_link):
    if t_o_link == "TOWest":
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&filter_selector0=adr&" \
              f"address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
              f"address_unit_selector0%5B%5D=2267&address_unit_selector0%5B%5D=0&filter_selector1=adr&" \
              f"address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
              f"address_unit_selector1%5B%5D=3215&address_unit_selector1%5B%5D=0&filter_selector2=adr&" \
              f"address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
              f"address_unit_selector2%5B%5D=2275&address_unit_selector2%5B%5D=0&filter_selector3=adr&" \
              f"address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
              f"address_unit_selector3%5B%5D=2261&address_unit_selector3%5B%5D=0&filter_selector4=adr&" \
              f"address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
              f"address_unit_selector4%5B%5D=2264&address_unit_selector4%5B%5D=0&filter_selector5=adr&" \
              f"address_unit_selector5%5B%5D=421&address_unit_selector5%5B%5D=426&" \
              f"address_unit_selector5%5B%5D=2276&address_unit_selector5%5B%5D=0&filter_selector6=adr&" \
              f"address_unit_selector6%5B%5D=421&address_unit_selector6%5B%5D=426&" \
              f"address_unit_selector6%5B%5D=2269&address_unit_selector6%5B%5D=0&filter_selector7=date_add&" \
              f"date_add7_value2=1&date_add7_date1={start_day}&date_add7_date2={date_now}&filter_group_by="

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
              f"address_unit_selector1%5B%5D=0&filter_selector2=adr&" \
              f"address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
              f"address_unit_selector2%5B%5D=2234&address_unit_selector2%5B%5D=0&filter_selector3=adr&" \
              f"address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
              f"address_unit_selector3%5B%5D=1944&address_unit_selector3%5B%5D=0&filter_selector4=adr&" \
              f"address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
              f"address_unit_selector4%5B%5D=2233&address_unit_selector4%5B%5D=0&filter_selector5=adr&" \
              f"address_unit_selector5%5B%5D=421&address_unit_selector5%5B%5D=426&" \
              f"address_unit_selector5%5B%5D=2235&address_unit_selector5%5B%5D=0&filter_group_by="

    elif t_o_link == "TONorth":
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&filter_selector0=adr&" \
              f"address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
              f"address_unit_selector0%5B%5D=2262&address_unit_selector0%5B%5D=0&filter_selector1=adr&" \
              f"address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
              f"address_unit_selector1%5B%5D=2232&address_unit_selector1%5B%5D=0&filter_selector2=adr&" \
              f"address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=426&" \
              f"address_unit_selector2%5B%5D=3229&address_unit_selector2%5B%5D=0&filter_selector3=adr&" \
              f"address_unit_selector3%5B%5D=421&address_unit_selector3%5B%5D=426&" \
              f"address_unit_selector3%5B%5D=2274&address_unit_selector3%5B%5D=0&filter_selector4=adr&" \
              f"address_unit_selector4%5B%5D=421&address_unit_selector4%5B%5D=426&" \
              f"address_unit_selector4%5B%5D=3277&address_unit_selector4%5B%5D=2252&" \
              f"address_unit_selector4%5B%5D=0&" \
              f"filter_selector5=adr&address_unit_selector5%5B%5D=421&" \
              f"address_unit_selector5%5B%5D=3253&" \
              f"address_unit_selector5%5B%5D=3277&address_unit_selector5%5B%5D=10010&" \
              f"address_unit_selector5%5B%5D=0&" \
              f"filter_selector6=date_add&" \
              f"date_add6_value2=1&date_add6_date1={start_day}&date_add6_date2={date_now}&filter_group_by="

    elif t_o_link == "TOEast":
        t_o_link = f"http://us.gblnet.net/oper/?core_section=customer_list&filter_selector0=adr&" \
              f"address_unit_selector0%5B%5D=421&address_unit_selector0%5B%5D=426&" \
              f"address_unit_selector0%5B%5D=2265&address_unit_selector0%5B%5D=0&filter_selector1=adr&" \
              f"address_unit_selector1%5B%5D=421&address_unit_selector1%5B%5D=426&" \
              f"address_unit_selector1%5B%5D=2268&address_unit_selector1%5B%5D=0&filter_selector2=adr&" \
              f"address_unit_selector2%5B%5D=421&address_unit_selector2%5B%5D=3253&" \
              f"address_unit_selector2%5B%5D=3277&address_unit_selector2%5B%5D=3411&" \
              f"address_unit_selector2%5B%5D=0&filter_selector3=date_add&date_add3_value2=1&" \
              f"date_add3_date1={start_day}&date_add3_date2={date_now}&filter_group_by="

    print(t_o_link)
    try:
        html = session_users.get(t_o_link)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
            table = soup.find_all('tr', class_="cursor_pointer")
            answer = parser_userside.save_from_userside(table, t_o)
            return answer
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        print(f'{t_o} : {e}')


# Парсер ГК за один день
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
                if area == "Кировский" or area == "Московский" or area == "Фрунзенский":
                    print("Есть спорные районы")
                    table = parser_goodscat.street_filter(table, t_o)
            answer = parser_goodscat.save_from_goodscat_for_day(table, status, date, area)
            return answer
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        link = url_link  # Заглушка ссылки для ошибки
        print(f'{link} : {e}')


# Парсер Нетаба
# Запуск из файла parser_goodscat.py
def parser_netup(gk_num):
    url_link = f"https://billing.athome.pro/payments.php?view={gk_num}&source=inet_dev"
    try:
        html = session_netup.get(url_link)
        if html.status_code == 200:
            soup = BeautifulSoup(html.text, 'lxml')
            # table1 = soup.find_all('tr', class_="zebra")
            table1 = soup.find_all("form", class_="")
            table2 = table1[2]
            table3 = table2.find_all('td', class_="")
            # print(table3)
            print(table3[3].text)  # Лицевой счет
            print(table3[81].input['value'])  # Мастер
            print(table3[145].input['value'])  # Метраж
            answer = [table3[3].text, table3[81].input['value'], table3[145].input['value']]
            return answer
        else:
            print("error")
    except requests.exceptions.TooManyRedirects as e:
        link = url_link  # Заглушка ссылки для ошибки
        print(f'{link} : {e}')


# Создадим папки для хранения отчетов, если их нет
def create_folder():
    if not os.path.exists(f"TOEast"):
        os.makedirs(f"TOEast")
    if not os.path.exists(f"TOWest"):
        os.makedirs(f"TOWest")
    if not os.path.exists(f"TONorth"):
        os.makedirs(f"TONorth")
    if not os.path.exists(f"TOSouth"):
        os.makedirs(f"TOSouth")


def main():
    # Автоматический запуск парсера по таймеру.
    # Время запуска берется из конфига(строка)
    schedule.every().day.at(config.time_for_start_parser).do(auto_report)
    # schedule.every(1).minutes.do(test_timer)
    while True:
        schedule.run_pending()
        # time.sleep(1)


if __name__ == '__main__':
    create_folder()
    print("Бот запущен")
    # Тестовая отправка сообщения в телеграм
    # test_timer()
    # executor.start_polling(dp, skip_updates=True)
    # auto_report()
    main()
