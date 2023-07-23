from datetime import datetime, timedelta

# from main import parser_netup
import to_exel

west_all_street = ["Канонерский остров", "Шотландская",
                   "Двинская", "Оборонная", "Смоленская",
                   "Тамбовская", "Турбинная", "Тосина", "Расстанная"]


def save_from_goodscat(table):
    arr = []
    print(f'Всего должно быть абонентов {len(table)}')
    for i in table:
        # !!!!!!!!!!!! Не ищет таймаут ?????????????
        user = []
        td_class_all = i.find_all('td', class_="")
        # У адреса другой класс
        address_class = i.find('td', class_="addr")
        # td_class_all[1] = Номер ГК

        user.append(td_class_all[9].text)  # 0 = Дата смены статуса???             # !!!!!! +1

        # Найдем и извлечем выбранный статус заявки
        # Статус может быть не опцией, а строкой
        if len(td_class_all[7].text) < 300:                 # !!!!!! +1
            # print(td_class_all[1].text)
            select = td_class_all[7].find('option', selected="selected")             # !!!!!! +1
            # print(select)
            user.append(select.text)  # 1 = !!! Статус заявки
        else:  # Вариант если нет select, в этом случае там куча пробелов и в конце текст
            user.append(td_class_all[7].text.strip())  # 1 = !!! Статус заявки             # !!!!!! +1
            print("Этот вариант")

        # Отдельно берем адрес, заодно уберем лишние пробелы по краям
        address = address_class.text.strip()
        user.append(address)  # 2 = Адрес

        user.append(td_class_all[1].text)  # 3 = Номер ГК
        user.append(td_class_all[4].text)  # 4 = Дата принятия заявки???   !!!!!! +1
        user.append(td_class_all[6].text)  # 5 = ФИО абонента              # !!!!!! +1
        user.append(td_class_all[10].text)  # 6 = Дата предполагаемого выполнения             # !!!!!! +1
        # user.append(td_class_all[10].text)  # 6 = !!! Район (Адмиралтейский-Кировский-Фрунзенский)

        arr.append(user)  # Добавим итог в общий массив с адресами
    return arr

# Функция сбора подключений из ГК за прошлый день. Различается по статусу
# def save_from_goodscat_for_day(table, status, date2, area):
#     arr = []
#     print(f'Всего должно быть абонентов {len(table)}')
#     for i in table:
#         user = []
#         td_class_all = i.find_all('td', class_="")
#         # print(f"td_class_all24146: {td_class_all}")
#         date1 = td_class_all[10].text[0:10]
#         # Первым делом отсеим даты, при статусе Архив
#         # Для статуса Архив, должна быть "вчерашняя" дата, то есть получаемая аргументом
#         # if status == "archive":
#         if date2 != date1:
#             continue
#
#         # У адреса другой класс
#         address_class = i.find('td', class_="addr")
#         # Тут нужно запустить парсер для Нетаба, но хз как его запускать отсюда
#         # user.append(td_class_all[1].text)  # 0 = Номер ГК
#         gk_num = td_class_all[1].text
#         print(f"Запускаем Нетаб, ищем пользователя: {gk_num}")
#         answer = parser_netup(gk_num)
#         # Нужно исключить заявки Горохова. Это мастер ИС
#         # Будем искать его в определенных районах
#         if area == "Красногвардейский":
#             if answer[1] == "ИС" or answer[1] == "И С":
#                 print(f"answer23451 {answer}")
#                 continue
#         print(f"answer156 {answer}")
#
#         user.append("ЭтХоум")  # Бренд
#
#         # У даты нужно обрезать время, заменить тире и развернуть
#         date1 = date1.split("-")
#         date1 = f"{date1[2]}.{date1[1]}.{date1[0]}"
#         user.append(date1)  # Дата
#
#         user.append(answer[0])  # Договор
#
#         # Отдельно берем адрес, заодно уберем лишние пробелы по краям
#         address = address_class.text.strip()
#         address = address.split(",")
#         # Тут придется вручную отсеивать поселки
#         if address[0] == "Парголово" or \
#                 address[0] == "Шушары" or \
#                 address[0] == "Мурино" or \
#                 address[0] == "Песочный" or \
#                 address[0] == "Новогорелово":
#             user.append(address[1].strip())  # Адрес. Тут еще раз сразу порежем пробелы по краям
#         else:
#             user.append(address[0])  # Адрес
#         user.append(address[-2][2:])  # Адрес. Тут видимо номер дома?
#         user.append(address[-1][4:])  # Адрес. А тут видимо номер квартиры?
#
#         user.append(answer[1])  # Мастер
#         user.append(area)  # Район
#         user.append(answer[2])  # Метраж
#
#         arr.append(user)  # Добавим итог в общий массив с адресами
#     return arr


# Отфильтруем чужие улицы спорных районов
def street_filter(table, t_o):
    new_table = []
    for i in table:
        # Найдем адрес по классу
        address_class = i.find('td', class_="addr")
        # Обрежем пробелы по краям
        address = address_class.text.strip()
        address = address.split(",")
        # print(f"Тут должен быть список частей адреса: {address}")
        if t_o == "TOWest":
            for street in west_all_street:  # Список улиц
                if street in address:
                    # print(f"Улица {address} найдена в списке")
                    new_table.append(i)
        elif t_o == "TOSouth":
            for a in address:  # Список улиц
                if a not in west_all_street:
                    new_table.append(i)
                    break
                else:
                    break
    return new_table
