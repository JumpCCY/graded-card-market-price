import requests
import re
import pandas as pd 
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


cards = []

csv_file = "cards_test.csv"

try:
    df = pd.read_csv(csv_file)
    print("Loaded existing table from CSV.")
except FileNotFoundError:
    df = pd.DataFrame(columns=["id", "name", "price"])
    print("Created new table.")

def request_card_price(id):
    base_url_1 = "https://pokeca-chart.com/ch/php/get.php"
    base_url_2 = "https://pokeca-chart.com/ch/php/get-item-btn-link.php"

    info_res = requests.get(base_url_2, params={"item_id": id}, timeout=10)
    info_data = info_res.json()
    if not info_data:
        return None, None

    price_res = requests.get(
        base_url_1, params={"function": "get_item_grd_info", "item_id": id},
        timeout=10
    )
    price_data = price_res.json()
    price_data = price_data[0]

    if not price_data:
        return None, None

    psa10_price_clean_jpy = re.sub(r"\D", "", price_data["recent_price_2"])

    if psa10_price_clean_jpy == "":
        psa10_price_clean_jpy = "0"

    return info_data["name"], int(psa10_price_clean_jpy)

def add_card_to_table(df, card_id, card_name, card_price, csv_file):
    new_row = {"id": card_id, "name": card_name, "price": card_price}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_file, index=False)
    return df

none_streak = 0
i = 1
write_lock = threading.Lock()


def fetch_batch(start_id, end_id, workers=10):
    global df, none_streak
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(request_card_price, i): i for i in range(start_id, end_id + 1)}
        for future in as_completed(futures):
            card_id = futures[future]
            try:
                name, price = future.result()
            except Exception as e:
                print(f"id {card_id}: error -> {e}")
                continue

            if name and price:
                none_streak = 0
                # protect concurrent writes to df / CSV
                with write_lock:
                    name = re.search(r'\[(.*?)\]', name).group(1)
                    df = add_card_to_table(df, card_id, name, price, csv_file)
                print(f"id {card_id}: added ({name}, {price} JPY)")
            else:
                none_streak += 1
                print(f"id {card_id}: skipped (no data)")

 
fetch_batch(1, 800, workers=10)

