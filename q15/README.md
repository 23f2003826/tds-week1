# Question 15: Acme Appliances Order Ledger Agent

## Overview
This directory contains the Acme Appliances Order Ledger Question-Answering Agent for Question 15 of IIT Madras TDS Week 1 Assignment.

- **Student Email**: `23f2003826@ds.study.iitm.ac.in`
- **Endpoint**: `POST /ledger` (also aliases `/q15`)
- **Payload**: `{"question": "..."}`
- **Response**: `{"answer": ...}`

## Architecture

1. **Data Ingestion & Normalization**:
   - Downloads export NDJSON from the unique exam question URL.
   - Deduplicates orders by order ID keeping the latest `updated_at`.
   - Converts dates to `Asia/Kolkata` timezone.
   - Populates SQLite `orders` table with precomputed monetary fields:
     - `amount_usd`
     - `revenue_usd` (only `status = 'paid'`)
     - `refund_usd` (only `status = 'refunded'`)
     - `order_date`, `year`, `month`, `month_name`, `quarter`

2. **Dual-Layer Query Engine**:
   - **Layer 1: In-Memory Cache**: Repeated or identical queries return in $0.0001$s with 0 token consumption.
   - **Layer 2: Fast Deterministic Regex**: Standard structured questions (region/month/year revenue, refunds, product counts) match regex patterns to direct SQL with 0 token consumption.
   - **Layer 3: Gemini 2.5 Flash**: Complex, varied, or novel natural language questions are translated to exact SQLite queries and executed safely in $< 1.5$s (well under the 15-second grader limit).

## Public Endpoint
```text
https://<YOUR-RENDER-SERVICE-NAME>.onrender.com/ledger
```

