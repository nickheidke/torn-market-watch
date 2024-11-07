import os
import requests
import pandas as pd
from data import WATCHED_ITEMS

def get_torn_api_key():
    api_key = os.getenv('TORN_API_KEY')
    if not api_key:
        raise EnvironmentError("TORN_API_KEY environment variable not set")
    return api_key

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
    all_data = []

    # Collect data for each item_id
    for item_id in WATCHED_ITEMS.values():
        market_data = get_market_data(item_id)
        all_data.extend(market_data)

    # Create a DataFrame from the collected data
    df = pd.DataFrame(all_data)

    # Group data by 'item_id' to calculate statistics
    grouped = df.groupby('item_id', group_keys=False).apply(
    lambda x: pd.Series({
        'average_price': (x['cost'] * x['quantity']).sum() / x['quantity'].sum(),
        'std_deviation': x['cost'].std(),
        'min_price': x['cost'].min(),
        'max_price': x['cost'].max(),
        'median_price': x['cost'].median(),
        'total_quantity': x['quantity'].sum()
    })
    ).reset_index()

    # Print statistics for each item_id
    for _, row in grouped.iterrows():
        item_name = [name for name, id in WATCHED_ITEMS.items() if id == row['item_id']][0]
        print(f"Item: {item_name}")
        print(f"  Average Price: ${row['average_price']:,.2f}")
        print(f"  Median Price: ${row['median_price']:,.2f}")
        print(f"  Standard Deviation: ${row['std_deviation']:,.2f}")
        print(f"  Min Price: ${row['min_price']:,.2f}")
        print(f"  Max Price: ${row['max_price']:,.2f}")
        print(f"  Total Quantity: {row['total_quantity']}\n")

        # Print each individual record for this item_id
        print(f"  Records for {item_name}:")
        item_records = df[df['item_id'] == row['item_id']]
        for _, record in item_records.iterrows():
            print(f"    Cost: ${record['cost']:,.2f}, Quantity: {record['quantity']}")
        
        # Filter for records where cost is below one standard deviation from the mean
        outliers = item_records[item_records['cost'] < row['average_price'] - row['std_deviation']]
        
        # Display records below one standard deviation, if any
        if not outliers.empty:
            print(f"\n  Records below one standard deviation for {item_name}:")
            for _, outlier in outliers.iterrows():
                print(f"    Cost: ${outlier['cost']:,.2f}, Quantity: {outlier['quantity']}")
        print()  # Blank line for readability between items

# Example usage
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
