# Вручную подсчитаем принятые заявки по группам

def calc_msg_report(table):
    # 0 - подключения интернет
    # Отказ (отказ от реализации, отказ клиента)
    # В работе КО (Отложено)
    # На другую дату (пусто)
    # 1 - подключение домофон
    # 2 - подключение тв
    # 3 - сервис интернет
    # 4 - сервис тв

    # 5 - подключения интернет ЭХ
    # Отказ = Отказ, НаОтказ
    # В работе КО (Тайм-аут, НаОбзвон, ПростоЗаявка, Дубль, Нестандарт, Неверный адрес, ЮрЛицо)
    # НетТехВозм (НетТехВозм)
    # На другую дату (Перенесено, Назначено, ПротПодкл)

    internet = 0
    internet_refusing = 0
    internet_in_work_co = 0
    internet_no_tech = 0
    internet_another_date = 0
    for i in table[0]:
        internet += 1
        if i[1].lower() == "отказ от реализации" \
                or i[1].lower() == "отказ клиента" \
                or i[1] == "НаОтказ" \
                or i[1].strip() == "Отказ":
            internet_refusing += 1
        elif i[1] == "Отложено" \
                or i[1] == "Тайм-аут" \
                or i[1] == "НаОбзвон" \
                or i[1] == "ПростоЗаявка" \
                or i[1] == "Дубль" \
                or i[1] == "Нестандарт" \
                or i[1] == "Неверный адрес" \
                or i[1] == "ЮрЛицо":
            internet_in_work_co += 1
        elif i[1] == "пусто" \
                or i[1] == "Перенесено" \
                or i[1] == "Назначено" \
                or i[1] == "ПротПодкл":
            internet_another_date += 1
        elif i[1] == "НетТехВозм":
            internet_no_tech += 1

    for i in table[5]:
        internet += 1
        if i[1].lower() == "отказ от реализации" \
                or i[1].lower() == "отказ клиента" \
                or i[1] == "НаОтказ" \
                or i[1].strip() == "Отказ":
            internet_refusing += 1
        elif i[1] == "Отложено" \
                or i[1] == "Тайм-аут" \
                or i[1] == "НаОбзвон" \
                or i[1] == "ПростоЗаявка" \
                or i[1] == "Дубль" \
                or i[1] == "Нестандарт" \
                or i[1] == "Неверный адрес" \
                or i[1] == "ЮрЛицо":
            internet_in_work_co += 1
        elif i[1] == "пусто" \
                or i[1] == "Перенесено" \
                or i[1] == "Назначено" \
                or i[1] == "ПротПодкл":
            internet_another_date += 1
        elif i[1] == "НетТехВозм":
            internet_no_tech += 1
    # ТВ
    tv = 0
    tv_refusing = 0
    tv_another_date = 0
    tv_in_work_co = 0
    for i in table[2]:
        tv += 1
        if i[1] == "отказ от реализации" \
                or i[1] == "Отказ клиента":
            tv_refusing += 1
        elif i[1] == "пусто":
            tv_another_date += 1
        elif i[1] == "Отложено":
            tv_in_work_co += 1

    # Домофон
    intercom = 0
    intercom_refusing = 0
    intercom_another_date = 0
    intercom_in_work_co = 0
    for i in table[1]:
        intercom += 1
        if i[1] == "отказ от реализации" \
                or i[1] == "Отказ клиента":
            intercom_refusing += 1
        elif i[1] == "пусто":
            intercom_another_date += 1
        elif i[1] == "Отложено":
            intercom_in_work_co += 1

    # Сервис интернет
    serv_internet = 0
    serv_internet_refusing = 0
    serv_internet_another_date = 0
    serv_internet_in_work_co = 0
    for i in table[3]:
        serv_internet += 1
        if i[1].lower() == "отказ от реализации" \
                or i[1].lower() == "отказ клиента":
            serv_internet_refusing += 1
        elif i[1] == "пусто":
            serv_internet_another_date += 1
        elif i[1] == "Отложено":
            serv_internet_in_work_co += 1
        elif i[1] == "Выполнено без участия ТО"\
                or i[1] == "Аренда/продажа при подключении":
            serv_internet -= 1

    # Сервис ТВ
    serv_tv = 0
    serv_tv_refusing = 0
    serv_tv_another_date = 0
    serv_tv_in_work_co = 0
    for i in table[4]:
        serv_tv += 1
        if i[1].lower() == "отказ от реализации" \
                or i[1].lower() == "отказ клиента":
            serv_tv_refusing += 1
        elif i[1] == "пусто":
            serv_tv_another_date += 1
        elif i[1] == "Отложено":
            serv_tv_in_work_co += 1
        elif i[1] == "Выполнено без участия ТО":
            serv_tv -= 1

    answer = f"\nИнтернет: \n" \
             f"Принято: {internet} \n" \
             f"Отказ: {internet_refusing} \n" \
             f"В работе КО: {internet_in_work_co} \n" \
             f"НетТехВозм: {internet_no_tech} \n" \
             f"На другую дату: {internet_another_date} \n \n" \
             f"ТВ: \n" \
             f"Принято: {tv} \n" \
             f"Отказ: {tv_refusing} \n" \
             f"На другую дату: {tv_another_date} \n" \
             f"В работе КО: {tv_in_work_co} \n \n" \
             f"Домофон: \n" \
             f"Принято: {intercom} \n" \
             f"Отказ: {intercom_refusing} \n" \
             f"На другую дату: {intercom_another_date} \n" \
             f"В работе КО: {intercom_in_work_co} \n \n" \
             f"Сервис интернет: \n" \
             f"Принято: {serv_internet} \n" \
             f"Отказ: {serv_internet_refusing} \n" \
             f"На другую дату: {serv_internet_another_date} \n" \
             f"В работе КО: {serv_internet_in_work_co} \n \n" \
             f"Сервис ТВ: \n" \
             f"Принято: {serv_tv} \n" \
             f"Отказ: {serv_tv_refusing} \n" \
             f"На другую дату: {serv_tv_another_date} \n" \
             f"В работе КО: {serv_tv_in_work_co} \n \n" \

    return answer

