import json
import sqlite3
import urllib.request
from datetime import datetime
import zoneinfo
from pathlib import Path

EXPORT_URL = (
    "https://exam.sanand.workers.dev/questionData?"
    "email=23f2003826%40ds.study.iitm.ac.in&"
    "quizSign=mT%2FVgcoJlvZhxOOJyxtdDBtugn%2FJ%2BQRam7dw3U00lXxF3nLm70%2BCgaFo%2FUQY%2BhZ%2Baia5sV4CK%2F9N8smazXFxQniakjYzLRw2%2BF82F6ZlZkhrpDjNNvJCuQeoZZegdSHApYbOsLgBUYQs%2Bijp0xvwGRjCk1OYic4aKGIuGZYFoi1WqJ4MTfDE7XXAd%2FtOgpNsiRgni6hbG97Tcy%2BAcjuhD0XHqNvvkaLq4mpukErQOwgSJCuQZ4bwmpSGmV5QuGsEgorWQxkkWNnUs9y97eI7nkmP9l4riLn1afxZDgY3g3XKojlkEvzBIYUuJWkOd71WBwfKfHCGvnnfHgMIR7JSYw%3D%3D&"
    "questionId=q-ledger-agent-server&path=%2Fexport"
)

RATES_URL = (
    "https://exam.sanand.workers.dev/questionData?"
    "email=23f2003826%40ds.study.iitm.ac.in&"
    "quizSign=mT%2FVgcoJlvZhxOOJyxtdDBtugn%2FJ%2BQRam7dw3U00lXxF3nLm70%2BCgaFo%2FUQY%2BhZ%2Baia5sV4CK%2F9N8smazXFxQniakjYzLRw2%2BF82F6ZlZkhrpDjNNvJCuQeoZZegdSHApYbOsLgBUYQs%2Bijp0xvwGRjCk1OYic4aKGIuGZYFoi1WqJ4MTfDE7XXAd%2FtOgpNsiRgni6hbG97Tcy%2BAcjuhD0XHqNvvkaLq4mpukErQOwgSJCuQZ4bwmpSGmV5QuGsEgorWQxkkWNnUs9y97eI7nkmP9l4riLn1afxZDgY3g3XKojlkEvzBIYUuJWkOd71WBwfKfHCGvnnfHgMIR7JSYw%3D%3D&"
    "questionId=q-ledger-agent-server&path=%2Frates"
)

DB_PATH = Path(__file__).resolve().parent / "ledger.db"

RATES = {
    "USD": 1.0,
    "EUR": 1.08,
    "INR": 0.01146
}

KOLKATA_TZ = zoneinfo.ZoneInfo("Asia/Kolkata")

def parse_iso_kolkata(ts_str: str) -> datetime:
    """Parses ISO timestamp string and converts it to Asia/Kolkata timezone."""
    # Replace 'Z' with '+00:00'
    if ts_str.endswith("Z"):
        ts_str = ts_str[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts_str)
    return dt.astimezone(KOLKATA_TZ)

def build_database(db_path: Path = DB_PATH) -> int:
    print(f"Fetching export data from {EXPORT_URL[:60]}...")
    req = urllib.request.Request(EXPORT_URL, headers={"User-Agent": "curl/8.0.0"})
    with urllib.request.urlopen(req) as resp:
        raw_ndjson = resp.read().decode("utf-8").strip()

    lines = raw_ndjson.split("\n")
    print(f"Downloaded {len(lines)} raw lines.")

    # Deduplicate keeping the latest updated_at
    latest_orders = {}
    for line in lines:
        if not line.strip():
            continue
        item = json.loads(line)
        oid = item["id"]
        if oid not in latest_orders or item["updated_at"] > latest_orders[oid]["updated_at"]:
            latest_orders[oid] = item

    print(f"Total deduplicated orders: {len(latest_orders)}")

    # Connect to SQLite
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE orders (
        id TEXT PRIMARY KEY,
        customer TEXT,
        region TEXT,
        product TEXT,
        qty INTEGER,
        unit_price REAL,
        amount REAL,
        currency TEXT,
        status TEXT,
        created_at TEXT,
        updated_at TEXT,
        order_date TEXT,
        year INTEGER,
        month INTEGER,
        month_name TEXT,
        quarter TEXT,
        usd_rate REAL,
        amount_usd REAL,
        revenue_usd REAL,
        refund_usd REAL
    );
    """)

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    rows_to_insert = []
    for order in latest_orders.values():
        dt = parse_iso_kolkata(order["created_at"])
        order_date = dt.strftime("%Y-%m-%d")
        year = dt.year
        month = dt.month
        month_name = month_names[month]
        quarter = f"Q{(month - 1) // 3 + 1}"

        currency = order["currency"].upper()
        rate = RATES.get(currency, 1.0)
        amount = float(order["amount"])
        amount_usd = round(amount * rate, 4)

        status = order["status"].lower()
        revenue_usd = amount_usd if status == "paid" else 0.0
        refund_usd = amount_usd if status == "refunded" else 0.0

        rows_to_insert.append((
            order["id"],
            order["customer"],
            order["region"],
            order["product"],
            int(order["qty"]),
            float(order["unit_price"]),
            amount,
            currency,
            status,
            order["created_at"],
            order["updated_at"],
            order_date,
            year,
            month,
            month_name,
            quarter,
            rate,
            amount_usd,
            revenue_usd,
            refund_usd
        ))

    cur.executemany("""
    INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
    """, rows_to_insert)

    conn.commit()
    conn.close()

    print(f"Successfully populated {len(rows_to_insert)} orders into {db_path}!")
    return len(rows_to_insert)

if __name__ == "__main__":
    build_database()

