# Question 8: Q1 2025 Regional Performance Metrics

Analyze sales transactions to calculate regional performance metrics for TechMart Electronics.

---

## 📋 Task Details

* **Input File**: `sales_data/sales_data.csv` (from `sales_data.zip`)
* **Filter Criteria**:
  * `city` = `"Mumbai"`
  * `month` = `"Feb"` (extracted from `date` in `YYYY-MMM-DD` format)
* **Metric Formula**: $\text{Revenue} = \sum (\text{quantity} \times \text{price})$
* **Required Output**: Total revenue rounded to nearest integer.

---

## 📊 Matching Transactions

| Line | Date | City | Product | Quantity | Unit Price | Total Row Revenue |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **24** | `2025-Feb-3` | Mumbai | Laptop | 9 | 312.93 | 2816.37 |
| **31** | `2025-Feb-7` | Mumbai | Laptop | 1 | 103.23 | 103.23 |

$$\text{Total Revenue} = 2816.37 + 103.23 = 2919.60$$

$$\text{Rounded to Nearest Integer} = \mathbf{2920}$$

---

## 🔑 Final Answer to Submit

```text
2920
```

---

## 🚀 How to Run

```bash
./q8/q8.sh
```
Or directly:
```bash
python3 q8/solution.py
```

