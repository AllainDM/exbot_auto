from datetime import datetime

import xlrd
import xlwt
# import openpyxl


# Наши улицы в "совместных" районах
moscow = [" Смоленская ул.", " Киевская ул."]
frunze = [" Тосина ул.", " Тамбовская ул."]
kirov = [" Канонерский о-в", " Шотландская ул.", " Двинская ул.", " Оборонная ул.",
         " Севастопольская ул.", " Турбинная ул.", " Гладкова ул."]

west_all_street_for_userside = [" Канонерский о-в", " Шотландская ул.", " Двинская ул.", " Оборонная ул.",
                                " Севастопольская ул.", " Турбинная ул.", " Гладкова ул.",
                                " Тосина ул.", " Тамбовская ул.",
                                " Смоленская ул.", " Киевская ул."]

filter_iss = [


]
def save_to_exel_from_userside(table_name, arr, t_o):
    t_o_rus = ""
    if t_o == "TOWest":
        t_o_rus = "ТО_Запад"
    elif t_o == "TONorth":
        t_o_rus = "ТО_Север"
    elif t_o == "TOSouth":
        t_o_rus = "ТО_Юг"
    elif t_o == "TOEast":
        t_o_rus = "ТО_Восток"
    wb = xlwt.Workbook()
    ws = wb.add_sheet(f'{table_name}')
    num_string = 2  # Стартовый номер строки для екселя
    for i in arr:
        print(f"список3143 {i}")
        ws.write(num_string, 0, i[0])  # Бренд
        ws.write(num_string, 1, i[1])  # Дата
        ws.write(num_string, 2, i[2])  # Номер договора
        ws.write(num_string, 3, i[3])  # Улица
        ws.write(num_string, 4, i[4])  # Дом
        ws.write(num_string, 5, i[5])  # Квартира
        ws.write(num_string, 6, i[6])  # Мастер
        ws.write(num_string, 7, i[7])  # Район
        ws.write(num_string, 10, i[8])  # Метраж
        num_string += 1

    num_string += 5
    ws.write(num_string, 1, "20.07.2023")
    ws.write(num_string + 1, 1, "20/07/2023")
    ws.write(num_string + 2, 1, "20-07-2023")

    date_now = datetime.now()
    ws.write(0, 0, f"Версия 005 Время: {date_now}")

    wb.save(f'{t_o}/{t_o_rus}_{table_name}.xls')


# Запись в ексель для недельного и месячного отчетов
# Аргументы: Название таблицы(дата), список(сам отчет), и ТО
def save_all_to_exel(table_name, arr, t_o):
    t_o_rus = ""
    if t_o == "TOWest":
        t_o_rus = "ТО_Запад"
    elif t_o == "TONorth":
        t_o_rus = "ТО_Север"
    elif t_o == "TOSouth":
        t_o_rus = "ТО_Юг"
    elif t_o == "TOEast":
        t_o_rus = "ТО_Восток"
    wb = xlwt.Workbook()
    ws = wb.add_sheet(f'{table_name}')
    # ws = wb.add_sheet(f'Неделя')
    num_string = 2  # Стартовый номер строки для екселя
    column = 16  # Стартовый столбец. Каждая таблица будет сдвигаться вправо
    result_string = 1  # Тут запись статистики
    for i in arr:
        print(i)
        for ii in i:
            ws.write(num_string, column, ii[0])
            ws.write(num_string, column + 1, ii[1])
            ws.write(num_string, column + 2, ii[2])
            ws.write(num_string, column + 3, ii[3])
            num_string += 1
        column += 6
        num_string = 2  # Обновим с новой строки

    # Нарисуем базовую "разметку"
    # Интернет
    ws.write(2, 0, "Интернет")
    ws.write(3, 0, "Поступило общее")
    ws.write(3, 2, xlwt.Formula('SUM(J3:J7)+SUM(K10:K13)'))
    # ws.write(4, 0, "Выполнено")
    # ws.write(4, 2, xlwt.Formula('J3+K10'))

    ws.write(1, 4, "Доступ")
    ws.write(1, 6, xlwt.Formula('J3'))
    ws.write(2, 4, "Отказ")
    ws.write(2, 6, xlwt.Formula('J4+K11'))
    ws.write(3, 4, "На другую дату")
    ws.write(3, 6, xlwt.Formula('J7+K13'))
    ws.write(4, 4, "В работе КО")
    ws.write(4, 6, xlwt.Formula('J5+K12'))

    ws.write(6, 4, "НетТехВозм")
    ws.write(6, 6, xlwt.Formula('J6'))

    # ws.write(9, 10, xlwt.Formula('COUNTIF(R2:R1000;"Выполнено"))'))
    # ws.write(10, 10, xlwt.Formula('COUNTIF(R2:R1000;"Отказ клиента")+COUNTIF(AR2:AR1000;"Отказ от реализации"))'))
    # ws.write(11, 10, xlwt.Formula('COUNTIF(R2:R1000;"Отложено"))'))
    # ws.write(12, 10, xlwt.Formula('COUNTIF(R2:R1000;"пусто"))'))
    # ТВ
    ws.write(16, 0, "ТВ")
    ws.write(17, 0, "Поступило общее")
    ws.write(17, 2, xlwt.Formula('COUNTA(AD3:AD1000)'))
    # ws.write(18, 0, "Выполнено")
    # ws.write(18, 2, xlwt.Formula('COUNTIF(AD3:AD1000;"Выполнено")'))

    # ws.write(15, 4, "Доступ")

    ws.write(16, 4, "Отказ")
    ws.write(16, 6, xlwt.Formula('COUNTIF(AD3:AD1000;"Отказ клиента") + COUNTIF(AD3:AD1000;"Отказ от реализации")'))
    ws.write(17, 4, "На другую дату")
    ws.write(17, 6, xlwt.Formula('COUNTIF(AD3:AD1000;"пусто")'))
    ws.write(18, 4, "В работе КО")
    ws.write(18, 6, xlwt.Formula('COUNTIF(AD3:AD1000;"Отложено")'))

    # Домофон

    ws.write(22, 0, "Домофон")
    ws.write(23, 0, "Поступило общее")
    ws.write(23, 2, xlwt.Formula('COUNTA(X3:X1000)'))
    # ws.write(24, 0, "Выполнено")
    # ws.write(24, 2, xlwt.Formula('COUNTIF(X3:X1000;"Выполнено")'))

    # ws.write(21, 4, "Доступ")

    ws.write(22, 4, "Отказ")
    ws.write(22, 6, xlwt.Formula('COUNTIF(X3:X1000;"Отказ клиента") + COUNTIF(X3:X1000;"Отказ от реализации")'))
    ws.write(23, 4, "На другую дату")
    ws.write(23, 6, xlwt.Formula('COUNTIF(X3:X1000;"пусто")'))
    ws.write(24, 4, "В работе КО")
    ws.write(24, 6, xlwt.Formula('COUNTIF(X3:X1000;"Отложено")'))

    # Сервис интернет
    ws.write(28, 0, "Сервис интернет")
    ws.write(29, 0, "Поступило общее")
    ws.write(29, 2, xlwt.Formula('COUNTA(AJ3:AJ1000) - '
                                 'COUNTIF(AJ3:AJ1000;"Выполнено без участия ТО") - '
                                 'COUNTIF(AJ3:AP1000;"Аренда/продажа при подключении")'))
    # ws.write(30, 0, "Выполнено")
    # ws.write(30, 2, xlwt.Formula('COUNTIF(AJ3:AJ1000;"Выполнено") + '
    #                              'COUNTIF(AJ3:AJ1000;"На проводку") + '
    #                              'COUNTIF(AJ3:AJ1000;"На списание")'))

    # ws.write(27, 4, "Доступ")

    ws.write(28, 4, "Отказ")
    ws.write(28, 6, xlwt.Formula('COUNTIF(AJ3:AJ1000;"Отказ клиента") + COUNTIF(AJ3:AJ1000;"Отказ от реализации")'))
    ws.write(29, 4, "На другую дату")
    ws.write(29, 6, xlwt.Formula('COUNTIF(AJ3:AJ1000;"пусто")'))
    ws.write(30, 4, "В работе КО")
    ws.write(30, 6, xlwt.Formula('COUNTIF(AJ3:AJ1000;"Отложено")'))

    # Сервис тв
    ws.write(34, 0, "Сервис тв")
    ws.write(35, 0, "Поступило общее")
    ws.write(35, 2, xlwt.Formula('COUNTA(AP3:AP1000) - COUNTIF(AP3:AP1000;"Выполнено без участия ТО")'))
    # ws.write(36, 0, "Выполнено")
    # ws.write(36, 2, xlwt.Formula('COUNTIF(AP3:AP1000;"Выполнено")'))

    # ws.write(33, 4, "Доступ")

    ws.write(34, 4, "Отказ")
    ws.write(34, 6, xlwt.Formula('COUNTIF(AP3:AP1000;"Отказ клиента") + COUNTIF(AP3:AP1000;"Отказ от реализации")'))
    ws.write(35, 4, "На другую дату")
    ws.write(35, 6, xlwt.Formula('COUNTIF(AP3:AP1000;"пусто")'))
    ws.write(36, 4, "В работе КО")
    ws.write(36, 6, xlwt.Formula('COUNTIF(AP3:AP1000;"Отложено")'))

    # Дорисуем интернет по провайдерам
    # ЭтХоум
    ws.write(0, 8, "ЭтХоум")
    ws.write(1, 8, "Подключено")
    ws.write(1, 9, xlwt.Formula(
        'COUNTIF(AV2:AV1000;"Архив")+'
        'COUNTIF(AV2:AV1000;"Подключен")+'
        'COUNTIF(AV2:AV1000;"Тариф")'))
    ws.write(1, 10, "(Архив, Подключен, Тариф)")

    ws.write(2, 8, "Доступ")
    ws.write(2, 9, xlwt.Formula('COUNTIF(AV2:AV1000;"НаОбзвон")'))
    ws.write(2, 10, "(НаОбзвон)")

    ws.write(3, 8, "Отказ")
    ws.write(3, 9, xlwt.Formula('COUNTIF(AV2:AV1000;"Отказ")+COUNTIF(AV2:AV1000;"НаОтказ")'))
    ws.write(3, 10, "(Отказ, НаОтказ)")

    ws.write(4, 8, "В работе КО")
    ws.write(4, 9, xlwt.Formula(
        'COUNTIF(AV2:AV1000;"Тайм-аут")+'
        'COUNTIF(AV2:AV1000;"ПростоЗаявка")+'
        'COUNTIF(AV2:AV1000;"Дубль")+'
        'COUNTIF(AV2:AV1000;"Нестандарт")+'
        'COUNTIF(AV2:AV1000;"ЮрЛицо")+'
        'COUNTIF(AV2:AV1000;"Неверный адрес")'))
    ws.write(4, 10, "(Тайм-аут, ПростоЗаявка, Дубль, Нестандарт, Неверный адрес, ЮрЛицо)")

    ws.write(5, 8, "НетТехВозм")
    ws.write(5, 9, xlwt.Formula('COUNTIF(AV2:AV1000;"НетТехВозм"))'))
    ws.write(5, 10, "(НетТехВозм)")

    ws.write(6, 8, "На другую дату")
    ws.write(6, 9, xlwt.Formula(
        'COUNTIF(AV2:AV1000;"Перенесено")+'
        'COUNTIF(AV2:AV1000;"Назначено")+'
        'COUNTIF(AV2:AV1000;"ПротПодкл"))'))
    ws.write(6, 10, "(Перенесено, Назначено, ПротПодкл)")

    # ЕТ + Тиера
    ws.write(8, 8, "ЕТ + Тиера")

    ws.write(9, 8, "Подключено")
    ws.write(9, 10, xlwt.Formula('COUNTIF(R2:R1000;"Выполнено"))'))
    ws.write(9, 11, "(Выполнено)")

    ws.write(10, 8, "Отказ")
    ws.write(10, 10, xlwt.Formula('COUNTIF(R2:R1000;"Отказ клиента")+COUNTIF(AR2:AR1000;"Отказ от реализации"))'))
    ws.write(10, 11, "(отказ от реализации, отказ клиента)")

    ws.write(11, 8, "В работе КО")
    ws.write(11, 10, xlwt.Formula('COUNTIF(R2:R1000;"Отложено"))'))
    ws.write(11, 11, "(Выполнено)")

    ws.write(12, 8, "На другую дату")
    ws.write(12, 10, xlwt.Formula('COUNTIF(R2:R1000;"пусто"))'))
    ws.write(12, 11, "(пусто)")

    date_now = datetime.now()
    ws.write(0, 0, f"Версия 004 Время: {date_now}")

    # wb.set_active_sheet("table_name")
    # wb.set_active_sheet(value=0)
    wb.save(f'{t_o}/{t_o_rus}_{table_name}.xls')



