
def cut_street(street):
    new_street = ""
    if street == "реки Смоленки":
        new_street = "Смоленки"
    elif street == "Набережная Фонтанки":
        new_street = "Фонтанки"
    elif street == "Канонерский остров":
        new_street = "Канонерский"
    elif street == "Воскресенская (Робеспьера)":
        new_street = "Воскресенская"
    elif street == "Петровская":
        new_street = "Петровская коса"

    else:
        new_street = street

    return new_street
