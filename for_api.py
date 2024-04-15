import json
import requests


def search_brand(ls):
    response = requests.get(f"https://api.billing.at-home.ru/siteid.php?ls={ls}&return=company_id")
    data = json.loads(response.content)
    print(f"data {data}")
    print(f' data["site_id"] {data["site_id"]}')
    if data["site_id"] == "1":
        return "Лана"
    elif data["site_id"] == "2":
        return "Невское"
