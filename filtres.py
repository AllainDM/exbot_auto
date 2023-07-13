
def cut_street(street):
    new_street = ""
    if street == "реки Смоленки":
        new_street = "Смоленки"
    elif street == "Набережная Фонтанки":
        new_street = "Фонтанки"
    elif street == "Канонерский остров":
        new_street = "Канонерский"

    else:
        new_street = street

    return new_street
