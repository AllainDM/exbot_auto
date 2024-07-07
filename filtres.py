
def cut_street(street):
    split_address = street.split(" ")
    lists = ["остров", "коса", "наб.", "пр.", "ул."]
    new_street = ""
    if split_address[-1] in lists:
        new_street = split_address[0]
    elif street == "Набережная Фонтанки":
        new_street = "Фонтанки"
    elif street == "Воронцовский бульвар":
        new_street = "Воронцовский"
    # elif street == "Канонерский остров":
    #     new_street = "Канонерский"
    elif street == "Воскресенская (Робеспьера)":
        new_street = "Воскресенская"
    # elif street == "Петровская":
    #     new_street = "Петровская коса"
    # elif street == "Октябрьская":
    #     new_street = "Октябрьская наб."
    # elif street == "Волковский пр.":
    #     new_street = "Волковский"

    else:
        new_street = street

    return new_street
