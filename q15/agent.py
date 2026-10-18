import json
import logging
import os
import re
import sqlite3
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
import zoneinfo
try:
    from fastapi import APIRouter, Request
    from fastapi.responses import JSONResponse
    router = APIRouter()
except ImportError:
    APIRouter = Any
    router = None

logger = logging.getLogger("q15_agent")
logger.setLevel(logging.INFO)

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(__file__).resolve().parent / "ledger.db"
KOLKATA_TZ = zoneinfo.ZoneInfo("Asia/Kolkata")

EXPORT_URL = (
    "https://exam.sanand.workers.dev/questionData?"
    "email=23f2003826%40ds.study.iitm.ac.in&"
    "quizSign=mT%2FVgcoJlvZhxOOJyxtdDBtugn%2FJ%2BQRam7dw3U00lXxF3nLm70%2BCgaFo%2FUQY%2BhZ%2Baia5sV4CK%2F9N8smazXFxQniakjYzLRw2%2BF82F6ZlZkhrpDjNNvJCuQeoZZegdSHApYbOsLgBUYQs%2Bijp0xvwGRjCk1OYic4aKGIuGZYFoi1WqJ4MTfDE7XXAd%2FtOgpNsiRgni6hbG97Tcy%2BAcjuhD0XHqNvvkaLq4mpukErQOwgSJCuQZ4bwmpSGmV5QuGsEgorWQxkkWNnUs9y97eI7nkmP9l4riLn1afxZDgY3g3XKojlkEvzBIYUuJWkOd71WBwfKfHCGvnnfHgMIR7JSYw%3D%3D&"
    "questionId=q-ledger-agent-server&path=%2Fexport"
)

RATES = {
    "USD": 1.0,
    "EUR": 1.08,
    "INR": 0.01146
}

# In-memory query cache to preserve API tokens
QUERY_CACHE: Dict[str, Any] = {}

def get_gemini_key() -> Optional[str]:
    """Retrieve Gemini API key from environment variable or .env file."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key.strip()
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None

def parse_iso_kolkata(ts_str: str) -> datetime:
    if ts_str.endswith("Z"):
        ts_str = ts_str[:-1] + "+00:00"
    return datetime.fromisoformat(ts_str).astimezone(KOLKATA_TZ)

def init_database():
    """Initializes and populates SQLite database if not present."""
    if DB_PATH.exists() and DB_PATH.stat().st_size > 10000:
        return

    logger.info("Downloading order ledger dataset...")
    req = urllib.request.Request(EXPORT_URL, headers={"User-Agent": "curl/8.0.0"})
    with urllib.request.urlopen(req) as resp:
        raw_ndjson = resp.read().decode("utf-8").strip()

    lines = raw_ndjson.split("\n")
    latest_orders = {}
    for line in lines:
        if not line.strip():
            continue
        item = json.loads(line)
        oid = item["id"]
        if oid not in latest_orders or item["updated_at"] > latest_orders[oid]["updated_at"]:
            latest_orders[oid] = item

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
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

    rows = []
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

        rows.append((
            order["id"], order["customer"], order["region"], order["product"],
            int(order["qty"]), float(order["unit_price"]), amount, currency,
            status, order["created_at"], order["updated_at"],
            order_date, year, month, month_name, quarter,
            rate, amount_usd, revenue_usd, refund_usd
        ))

    cur.executemany("INSERT OR REPLACE INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);", rows)
    conn.commit()
    conn.close()
    logger.info(f"Database initialized with {len(rows)} orders.")

# Initialize at module load
try:
    init_database()
except Exception as e:
    logger.error(f"Database init deferred: {e}")

def execute_sql(sql: str) -> Any:
    """Executes a SELECT query on SQLite and returns clean scalar result."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    val = row[0]
    if isinstance(val, float):
        return round(val, 2)
    return val

PRODUCTS = ['Air Fryer', 'Blender', 'Grinder', 'Juicer', 'Kettle', 'Mixer', 'Rice Cooker', 'Toaster']
REGIONS = ['Central', 'East', 'North', 'South', 'West']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def fast_rule_based_sql(question: str) -> Optional[str]:
    """Instant regex pattern matcher for common questions to save LLM tokens."""
    ql = question.lower()
    
    # Extract entities
    prod = next((p for p in PRODUCTS if p.lower() in ql), None)
    region = next((r for r in REGIONS if re.search(r'\b' + r.lower() + r'\b', ql)), None)
    month = next((m for m in MONTHS if m.lower() in ql), None)
    qm = re.search(r'\bq([1-4])\b', ql)
    quarter = f"Q{qm.group(1)}" if qm else None
    ym = re.search(r'\b(202[0-9])\b', ql)
    year = int(ym.group(1)) if ym else None
    cust_m = re.search(r'\b(c\d{4})\b', ql)
    customer = cust_m.group(1).upper() if cust_m else None

    # Base filters for general queries
    filters = []
    if prod: filters.append(f"product = '{prod}'")
    if region: filters.append(f"region = '{region}'")
    if month: filters.append(f"month_name = '{month}'")
    if quarter: filters.append(f"quarter = '{quarter}'")
    if year: filters.append(f"year = {year}")
    if customer: filters.append(f"customer = '{customer}'")
    where_clause = (" WHERE " + " AND ".join(filters)) if filters else ""

    # 1. "Which product" / "What product"
    if re.search(r'(which|what) product', ql):
        if 'refund' in ql:
            return "SELECT product FROM orders WHERE status = 'refunded' GROUP BY product ORDER BY SUM(refund_usd) DESC LIMIT 1;"
        elif any(k in ql for k in ['unit', 'sold', 'quantity', 'volume']):
            if any(k in ql for k in ['least', 'lowest', 'fewest']):
                return "SELECT product FROM orders WHERE status = 'paid' GROUP BY product ORDER BY SUM(qty) ASC LIMIT 1;"
            return "SELECT product FROM orders WHERE status = 'paid' GROUP BY product ORDER BY SUM(qty) DESC LIMIT 1;"
        else: # revenue
            if any(k in ql for k in ['least', 'lowest']):
                return "SELECT product FROM orders WHERE status = 'paid' GROUP BY product ORDER BY SUM(revenue_usd) ASC LIMIT 1;"
            return "SELECT product FROM orders WHERE status = 'paid' GROUP BY product ORDER BY SUM(revenue_usd) DESC LIMIT 1;"

    # 2. "Which region" / "What region"
    if re.search(r'(which|what) region', ql):
        if 'refund' in ql:
            return "SELECT region FROM orders WHERE status = 'refunded' GROUP BY region ORDER BY SUM(refund_usd) DESC LIMIT 1;"
        else:
            if any(k in ql for k in ['least', 'lowest']):
                return "SELECT region FROM orders WHERE status = 'paid' GROUP BY region ORDER BY SUM(revenue_usd) ASC LIMIT 1;"
            return "SELECT region FROM orders WHERE status = 'paid' GROUP BY region ORDER BY SUM(revenue_usd) DESC LIMIT 1;"

    # 3. "Which customer" / "What customer"
    if re.search(r'(which|what) customer', ql):
        if 'refund' in ql:
            return "SELECT customer FROM orders WHERE status = 'refunded' GROUP BY customer ORDER BY SUM(refund_usd) DESC LIMIT 1;"
        else:
            return "SELECT customer FROM orders WHERE status = 'paid' GROUP BY customer ORDER BY SUM(revenue_usd) DESC LIMIT 1;"

    # 4. "Which month" / "What month"
    if re.search(r'(which|what) month', ql):
        if 'refund' in ql:
            return "SELECT month_name FROM orders WHERE status = 'refunded' GROUP BY month, month_name ORDER BY SUM(refund_usd) DESC LIMIT 1;"
        else:
            return "SELECT month_name FROM orders WHERE status = 'paid' GROUP BY month, month_name ORDER BY SUM(revenue_usd) DESC LIMIT 1;"

    # 5. Units sold / quantity
    if 'unit' in ql or ('how many' in ql and any(k in ql for k in ['sold', 'ordered', 'purchased'])):
        if prod:
            base_f = [f"product = '{prod}'", "status = 'paid'"]
            if month: base_f.append(f"month_name = '{month}'")
            if quarter: base_f.append(f"quarter = '{quarter}'")
            if year: base_f.append(f"year = {year}")
            if region: base_f.append(f"region = '{region}'")
            return f"SELECT SUM(qty) FROM orders WHERE {' AND '.join(base_f)};"

    # 6. Customer count / unique customers
    if 'unique customer' in ql or 'how many customer' in ql:
        base_f = ["status = 'paid'"] if any(k in ql for k in ['paid', 'purchase', 'order']) else []
        if region: base_f.append(f"region = '{region}'")
        wh = (" WHERE " + " AND ".join(base_f)) if base_f else ""
        return f"SELECT COUNT(DISTINCT customer) FROM orders{wh};"

    # 7. Order counts
    if re.search(r'(how many|total).*?orders', ql):
        if 'refund' in ql:
            base_f = ["status = 'refunded'"]
        elif 'void' in ql:
            base_f = ["status = 'void'"]
        elif 'paid' in ql:
            base_f = ["status = 'paid'"]
        else:
            base_f = []
        if region: base_f.append(f"region = '{region}'")
        if customer: base_f.append(f"customer = '{customer}'")
        if month: base_f.append(f"month_name = '{month}'")
        if year: base_f.append(f"year = {year}")
        wh = (" WHERE " + " AND ".join(base_f)) if base_f else ""
        return f"SELECT COUNT(*) FROM orders{wh};"

    # 8. Refunds
    if 'refund' in ql:
        return f"SELECT ROUND(SUM(refund_usd), 2) FROM orders{where_clause};"

    # 9. Revenue / Spent / Amount
    if any(k in ql for k in ['revenue', 'spend', 'spent', 'amount']):
        return f"SELECT ROUND(SUM(revenue_usd), 2) FROM orders{where_clause};"

    return None

def gemini_text_to_sql(question: str, api_key: str) -> str:
    """Uses Gemini 2.5 Flash to convert arbitrary natural language to SQLite query."""
    prompt = f"""You are a SQLite expert. Convert this question into a single valid SQLite query against the `orders` table.

Schema of `orders`:
- id TEXT
- customer TEXT (e.g. 'C1022')
- region TEXT ('North', 'South', 'East', 'West', 'Central')
- product TEXT ('Mixer', 'Grinder', 'Kettle', 'Toaster', 'Air Fryer', 'Juicer', 'Blender', 'Rice Cooker')
- qty INTEGER
- unit_price REAL
- amount REAL (in local currency)
- currency TEXT ('USD', 'EUR', 'INR')
- status TEXT ('paid', 'refunded', 'void')
- order_date TEXT ('YYYY-MM-DD' in Asia/Kolkata)
- year INTEGER (e.g. 2026)
- month INTEGER (1-12)
- month_name TEXT ('January', 'February', 'March', 'April', 'May', 'June')
- quarter TEXT ('Q1', 'Q2')
- amount_usd REAL
- revenue_usd REAL (amount_usd if status='paid' else 0)
- refund_usd REAL (amount_usd if status='refunded' else 0)

Rules:
1. "Revenue" MUST use `revenue_usd` (or status='paid').
2. "Refunds" MUST use `refund_usd` (or status='refunded').
3. Money is in USD: use ROUND(..., 2).
4. Product names MUST be exact: 'Mixer', 'Grinder', 'Kettle', 'Toaster', 'Air Fryer', 'Juicer', 'Blender', 'Rice Cooker'.
5. Return ONLY the raw SQL query. No markdown, no quotes, no explanation.

Question: {question}
SQL:"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 500
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        sql_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Clean markdown codeblocks if present
        sql_text = re.sub(r"^```(sql)?", "", sql_text, flags=re.IGNORECASE).strip()
        sql_text = re.sub(r"```$", "", sql_text).strip()
        return sql_text

def answer_question(question: str) -> Any:
    """Answers an arbitrary question about Acme Appliances order ledger."""
    clean_q = question.strip()
    cache_key = clean_q.lower()
    if cache_key in QUERY_CACHE:
        logger.info(f"Cache hit for: {clean_q}")
        return QUERY_CACHE[cache_key]

    # Step 1: Try fast rule-based SQL
    sql = fast_rule_based_sql(clean_q)
    if sql:
        logger.info(f"Rule-based SQL: {sql}")
        ans = execute_sql(sql)
        QUERY_CACHE[cache_key] = ans
        return ans

    # Step 2: Use Gemini LLM to generate SQL
    api_key = get_gemini_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    logger.info(f"Calling Gemini for: {clean_q}")
    sql = gemini_text_to_sql(clean_q, api_key)
    logger.info(f"Gemini SQL: {sql}")
    ans = execute_sql(sql)
    QUERY_CACHE[cache_key] = ans
    return ans

if router is not None:
    @router.post("/ledger")
    @router.post("/ledger/")
    @router.post("/q15")
    @router.post("/q15/")
    async def ledger_endpoint(request: Request):
        try:
            body = await request.json()
            question = body.get("question", "")
            if not question:
                return JSONResponse(status_code=400, content={"error": "Field 'question' is required"})

            ans = answer_question(question)
            return {"answer": ans}
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return JSONResponse(status_code=500, content={"error": str(e)})

    @router.get("/ledger")
    @router.get("/q15")
    def ledger_status():
        return {
            "status": "online",
            "service": "Acme Appliances Order Ledger Agent",
            "endpoint": "/ledger"
        }
