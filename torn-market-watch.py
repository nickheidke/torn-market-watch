import os
import requests

from data import WATCHED_ITEMS

def get_torn_api_key():
    try:
        api_key = os.getenv('TORN_API_KEY')
        if not api_key:
            raise EnvironmentError("TORN_API_KEY environment variable not set")
        return api_key
    except EnvironmentError as e:
        print(e)


def get_market_data(item_id):
    api_key = get_torn_api_key()
    url = f"https://api.torn.com/market/{item_id}?selections=bazaar&key={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()
    data = response.json()
    bazaar_data = data.get('bazaar', [])

    parsed_data = [
        {
            'item_id': item_id,
            'cost': item['cost'],
            'quantity': item['quantity']
        }
        for item in bazaar_data
    ]
    return parsed_data

def main():
    for item_id in WATCHED_ITEMS.values():
        market_data = get_market_data(item_id)

        for entry in market_data:
            print(entry)


# Example usage
if __name__ == "__main__":
    main()