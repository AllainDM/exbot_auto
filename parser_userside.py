import time
import json
from datetime import datetime

import xlrd
import xlwt

import filtres
import to_json

# Наши улицы в "совместных" районах
south_in_moscow = [" Среднерогатская ул.", " Пулковское ш.",
                   " Витебский пр.", " Георгия Гречко ул.", " Дунайский пр.", " Звездная ул.",
                   " Космонавтов пр.", " Меридианная ул.", " Московское ш.", " Орбитальная ул.",
                   " Орджоникидзе ул.", " Пулковская ул.", " Струве ул.", " Типанова ул.",
                   " 1-й Предпортовый проезд", " 2-й Предпортовый проезд", ]
south_in_frunze = [" Белградская ул.", " Димитрова ул.", " Загребский б-р",
                   " Малая Каштановая ал.", " Славы пр."]
west_in_kirov = [" Канонерский о-в", " Шотландская ул.", " Двинская ул.", " Оборонная ул.",
                 " Севастопольская ул.", " Турбинная ул.", " Гладкова ул.", " Швецова ул."]


def save_from_userside(table, t_o):
    # table = table.reverse()
    # Для разворота можно все сделать в виде списка внутри списка, который и развернуть
    table_list_et = []  # Список для Е телекома
    table_list_tiera = []  # Список для Тиеры
    table_list_at_home = []  # Список для ЭтХоума
    dict_to_json = {}

    for i in table:
        # e_telecom = "ЕТ"
        brend = "ЕТ"
        one_list = []
        one_list_tiera = []
        one_list_at_home = []
        # Нужно найти элемент с фамилией мастера и номер договора.
        # 2: мастер, 3: номер договора
        td_class_all = i.find_all('td', class_="")
        pact = td_class_all[3].text
        soname = td_class_all[2].text
        soname = soname.split()
        # Без фамилии Тиера, но заявка нужна
        if not soname:
            soname = [" "]

        # Тут должна быть дата
        td_class_div_center = i.find_all('td', class_="div_center")
        # По длине даты можно отсортировать лишние задания
        date = td_class_div_center[-1].text
        date = date.split()
        if not date:
            if pact[0:2] == "40":
                brend = "Тиера"
            else:
                continue
        elif len(date[0]) == 10:
            pass
        elif len(date[0]) == 17:
            if date[0][0:2] == "12":
                pact = date[0][0:7]
                date = date[0][7:]
                brend = "ЭтХоум"
            else:
                continue
        else:
            continue
        if not date and soname == " ":
            print("нет ни мастера ни даты")
            continue

        # В ссылках хранится адрес, ищем ссылки
        list_a = i.find_all('a')  # Ищем ссылки во всей таблице
        # print(f"list_a {list_a}")
        # Адрес теперь почему-то может находиться под разным индексом. Будем искать совпадение по длинне
        address = []
        for num, el in enumerate(list_a):
            # print(el.text)
            if len(el.text) > 10:
                # print(f"Нужный элемент {el.text} под индексом {num}")
                address = list_a[num].text

        # print(f"address {list_a[2].text}")
        russia = address.replace(",", " ")
        address = address.split(",")
        # print(f"address {address}")

        # Отдельно сразу запишем район
        # district_arr = address[2].split(" ")
        # print(f"district_arr {district_arr}")
        # Почему оно не активно и что это? Тут пустое значение
        # district = district_arr[0]
        # print(f"district_arr[0] {district_arr[0]}")

        district = address[2][1:-4].strip()
        # print(f"district = address[2][1:-4] {address[2][1:-4]}")
        # Исключения
        if district == "Кол":
            district = "Колпино"
        elif district == "Пу":
            district = "Пушкин"
        elif district == "Ломон":
            district = "Ломоносов"

        # Разберем улицу, для определения поселков.
        if address[3] == " Парголово" or \
                address[3] == " Шушары" or \
                address[3] == " Новое Девяткино дер." or \
                address[3] == " пос. Шушары" or \
                address[3] == " Кудрово" or \
                address[3] == " Мурино" or \
                address[3] == " Бугры пос." or \
                address[3] == " Репино" or \
                address[3] == " Сестрорецк" or \
                address[3] == " Песочный" or \
                address[3] == " Лисий" or \
                address[3] == " Горелово" or \
                address[3] == " Коммунар" or \
                address[3] == " Колпино" or \
                address[3] == " Горская" or \
                address[3] == " Понтонный" or \
                address[3] == " Тельмана" or \
                address[3] == " Тельмана пос." or \
                address[3] == " Стрельна" or \
                address[3] == " пос. Стрельна" or \
                address[3] == " Новогорелово":
            street = address[4][1:-4]
            if address[4][-2] == 'ш':
                street = address[4][1:-3]
        else:
            # Обычно в конце строки "ул." или "б-р", тоесть 3 символа, но есть варианты с "ш."
            street = address[3][1:-4]
            if address[3][-2] == 'ш':
                street = address[3][1:-3]

        # Отдельно для Кудрово у ЕТ пропишем район как Кудрово
        if address[3] == " Кудрово":
            district = "Кудрово"

        # print(f"t_o {t_o}")
        # print(f"district {district}")
        if t_o == "TOEast" and district == "Всеволожский":
            print(f"ТОВосток и Всеволожский район: {district}")
            continue
        elif t_o == "TONorth" and district == "Кудрово":
            print(f"ТОСевер и Кудрово: {district}")
            continue
        # else:
        #     print(f"НЕ ТОВосток или Всеволожский район: {district}")

        # Дальше отфильтруем улицу на лишние слова общим фильтром
        street = street.strip()
        street = filtres.cut_street(street)

        # street = address[3][1:-4]
        # street = address[-2][1:-3]
        # pars_street = address[3][1:-4].split(" ")
        # pars_street = address[-2][1:-4]

        # address_dom = address[4].split()
        address_dom = address[-1].split()
        address_dom = address_dom[0]

        # Если поселок, то все сьезжает
        # if "пос." in pars_street or \
        #         "Куд" in pars_street or \
        #         "Му" in pars_street or \
        #         "Парго" in pars_street or \
        #         "Девяткино" in pars_street:
        #     # street = address[4][1:-4]
        #     street = address[-2][1:-4]
        #     address_dom = address[5].split()
        #     address_dom = address_dom[0]
        # print(pars_street)

        # Ищем номер дома, при двойном адресе берем номер дома перед "вторым" адресом
        # russia = address.replace(",", " ")
        russia = russia.split(" ")
        print(f"russia {russia}")
        russia_count = russia.count("Россия")
        print(f"russia_count {russia_count}")

        address_dom = ""

        if russia_count > 1:
            count_r = 0
            for num, el in enumerate(russia):
                print(f"el: {el}")
                if el == "Россия" and count_r == 1:
                    print(f"Найдено второе совпадение, номер элемента: {num}")
                    address_dom = russia[num - 2]
                    break
                elif el == "Россия":
                    count_r += 1
        else:
            address_dom = address[-1].split()
            print(f"address_dom {address_dom}")
            address_dom = address_dom[0]
            print(f"address_dom {address_dom}")

        # Отдельно надо разделить номер дома и квартиру
        if address_dom[-1].isdigit():
            address_dom = address_dom.replace("/", "к")
        else:
            address_dom = address_dom.replace("/", "")
        address_kv = address[-1].split()

        # Вычеркнем лишние улицы из "совместных" районов
        # Нужен хелп по улицам, ответ бота при запросе. Сделать улицы переменными, может в списке
        # Подходит ли улица под ТО, если нет, ниже будет пропуск в цикле
        street_is_norm = True
        if t_o == "TOWest":
            print(f"ТО Запад, сверяем {address}")
            if district == "Кировский":
                for our_street in west_in_kirov:
                    # if our_street in address:
                    if our_street in address:
                        street_is_norm = True
                        break
                    else:
                        street_is_norm = False
            elif district == "Фрунзенский":
                for our_street in south_in_frunze:
                    if our_street in address:
                        street_is_norm = False
                        break
                    else:
                        street_is_norm = True
            elif district == "Московский":
                for our_street in south_in_moscow:
                    if our_street in address:
                        street_is_norm = False
                        break
                    else:
                        street_is_norm = True
        if t_o == "TOSouth":
            print(f"ТО Юг, сверяем {address}")
            if district == "Кировский":
                for our_street in west_in_kirov:
                    # if our_street in address:
                    if our_street in address:
                        street_is_norm = False
                        break
                    else:
                        street_is_norm = True
            elif district == "Фрунзенский":
                for our_street in south_in_frunze:
                    if our_street in address:
                        street_is_norm = True
                        break
                    else:
                        street_is_norm = False
            elif district == "Московский":
                for our_street in south_in_moscow:
                    # if our_street in address:
                    if our_street in address:
                        street_is_norm = True
                        break
                    else:
                        street_is_norm = False
        if not street_is_norm:
            continue

        if brend == "ЕТ":
            one_list.append(brend)  # Бренд
            one_list.append(date)  # Дата
            one_list.append(pact.rstrip())   # Номер договора
            one_list.append(street)  # Улица
            try:
                one_list.append(int(address_dom))  # Дом
            except ValueError:
                one_list.append(address_dom)
            try:
                one_list.append(int(address_kv[-1]))  # Квартира
            except ValueError:
                one_list.append(address_kv[-1])  # Квартира
            one_list.append(soname[0])  # Мастер
            one_list.append(district)  # Район
            one_list.append(" ")  # Метраж

            table_list_et.append(one_list)

            # Сохраним в json
            # dict_to_json[]

        elif brend == "Тиера":
            one_list_tiera.append(brend)  # Бренд
            one_list_tiera.append(date)  # Дата
            one_list_tiera.append(int(pact.rstrip()))  # Номер договора
            one_list_tiera.append(street)  # Улица
            try:
                one_list_tiera.append(int(address_dom))  # Дом
            except ValueError:
                one_list_tiera.append(address_dom)
            try:
                one_list_tiera.append(int(address_kv[-1]))  # Квартира
            except ValueError:
                one_list_tiera.append(address_kv[-1])  # Квартира

            # one_list_tiera.append(address_dom)  # Дом
            # one_list_tiera.append(address_kv[-1])  # Квартира

            one_list_tiera.append(soname[0])  # Мастер
            one_list_tiera.append(district)  # Район
            one_list_tiera.append(" ")  # Метраж

            table_list_tiera.append(one_list_tiera)

    # Не добавляем ЭтХоум, он будет браться из другого парсера
        # else:  # Остальное видимо относится к ЭтХоуму
        #     one_list_at_home.append(brend)  # Бренд
        #     one_list_at_home.append(date)  # Дата
        #     one_list_at_home.append(pact)  # Номер договора
        #     one_list_at_home.append(street)  # Улица
        #     one_list_at_home.append(address_dom)  # Дом
        #     one_list_at_home.append(address_kv[-1])  # Квартира
        #     one_list_at_home.append(soname[0])  # Мастер
        #     one_list_at_home.append(district)  # Район
        #     one_list_at_home.append(" ")  # Метраж
        #
        #     table_list_at_home.append(one_list_at_home)

    # Пока не переворачиваем, чтоб удобнее сравнивать
    table_list_et.reverse()
    table_list_tiera.reverse()
    table_list_at_home.reverse()

    answer = table_list_et + table_list_tiera + table_list_at_home
    return answer

    # for i in table_list_et:
    #     ws.write(num_string, 0, i[0])  # Бренд
    #     ws.write(num_string, 1, i[1])  # Дата
    #     ws.write(num_string, 2, i[2])  # Номер договора
    #     ws.write(num_string, 3, i[3])  # Улица
    #     ws.write(num_string, 4, i[4])  # Дом
    #     ws.write(num_string, 5, i[5])  # Квартира
    #     ws.write(num_string, 6, i[6])  # Мастер
    #     ws.write(num_string, 7, i[7])  # Район
    #     num_string += 1
    #
    # num_string += 1
    # for i in table_list_tiera:
    #     ws.write(num_string, 0, i[0])  # Бренд
    #     ws.write(num_string, 1, i[1])  # Дата
    #     ws.write(num_string, 2, i[2])  # Номер договора
    #     ws.write(num_string, 3, i[3])  # Улица
    #     ws.write(num_string, 4, i[4])  # Дом
    #     ws.write(num_string, 5, i[5])  # Квартира
    #     ws.write(num_string, 6, i[6])  # Мастер
    #     ws.write(num_string, 7, i[7])  # Район
    #     num_string += 1
    #
    # num_string += 1
    # for i in table_list_at_home:
    #     ws.write(num_string, 0, i[0])  # Бренд
    #     ws.write(num_string, 1, i[1])  # Дата
    #     ws.write(num_string, 2, i[2])  # Номер договора
    #     ws.write(num_string, 3, i[3])  # Улица
    #     ws.write(num_string, 4, i[4])  # Дом
    #     ws.write(num_string, 5, i[5])  # Квартира
    #     ws.write(num_string, 6, i[6])  # Мастер
    #     ws.write(num_string, 7, i[7])  # Район
    #     num_string += 1


# Отфильтруем чужие улицы спорных районов, а так же правильно пропишем поселки
def street_filter(table):
    # new_table = []
    new_table = table
    # for i in table:
    #     # Найдем адрес по классу
    #     address_class = i.find('td', class_="addr")
    #     # Обрежем пробелы по краям
    #     address = address_class.text.strip()
    #     address = address.split(",")
    #     # print(f"Тут должен быть список частей адреса: {address}")
    #     for street in west_all_street:  # Список улиц
    #         if street in address:
    #             # print(f"Улица {address} найдена в списке")
    #             new_table.append(i)
    #         # else:
    #         #     pass
    return new_table
