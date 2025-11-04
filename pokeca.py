import requests
import re


cards = []


def request_card_price(id):
    base_url_1 = "https://pokeca-chart.com/ch/php/get.php"
    base_url_2 = "https://pokeca-chart.com/ch/php/get-item-btn-link.php"

    info_res = requests.get(base_url_2, params={"item_id": id}, timeout=5)
    info_data = info_res.json()
    if not info_data:
        return None, None

    price_res = requests.get(
        base_url_1, params={"function": "get_item_grd_info", "item_id": id},
        timeout=5
    )
    price_data = price_res.json()
    price_data = price_data[0]

    if not price_data:
        return None, None

    psa10_price_clean_jpy = re.sub(r"\D", "", price_data["recent_price_2"])

    return info_data["name"], int(psa10_price_clean_jpy)

none_streak = 0
# i = 1
# while True:
#     results = request_card_price(i)
#     if results is None:
#         print(f"Loop stopping at id{i} JSON returning false")
#         break

#     card_name, card_price = results

#     card_dict = {
#         "id": i,
#         "name": card_name,
#         "price": card_price
#     }

#     cards.append(card_dict)
#     i += 1



for i in range(1, 20):
    if none_streak > 10:
        break

    results = request_card_price(i)

    card_name, card_price = results

    card_dict = {
        "id": i,
        "name": card_name,
        "price": card_price
    }

    if card_name is not None or card_price is not None:
        none_streak = 0
        cards.append(card_dict)
        print(f"id {i} : added")
    else:
        none_streak += 1
        print(f"id {i} : returns none, passing")

print(cards)
