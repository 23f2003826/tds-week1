import csv
from pathlib import Path

# Path to the dataset
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "sales_data" / "sales_data.csv"

def calculate_mumbai_feb_revenue():
    total_revenue = 0.0
    matching_rows = []

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_parts = row["date"].split("-")
            month = date_parts[1]
            city = row["city"]

            # Filter by: city = "Mumbai" AND month = "Feb"
            if city == "Mumbai" and month == "Feb":
                quantity = int(row["quantity"])
                price = float(row["price"])
                revenue = quantity * price
                total_revenue += revenue
                matching_rows.append({
                    "date": row["date"],
                    "city": row["city"],
                    "product": row["product"],
                    "quantity": quantity,
                    "price": price,
                    "revenue": revenue
                })

    print(f"Matching Transactions ({len(matching_rows)} found):")
    for r in matching_rows:
        print(f"  Date: {r['date']} | Product: {r['product']} | Qty: {r['quantity']} | Price: {r['price']} | Row Revenue: {r['revenue']:.2f}")

    rounded_revenue = round(total_revenue)
    print("\n--- Summary ---")
    print(f"Exact Total Revenue:   {total_revenue:.2f}")
    print(f"Rounded Total Revenue: {rounded_revenue}")
    return rounded_revenue

if __name__ == "__main__":
    calculate_mumbai_feb_revenue()

