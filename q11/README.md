# Question 11: Cosine Similarity Search (VecSearch Labs)

Implement cosine similarity ranking over precomputed 64-dimensional embeddings for 250 documents and 10 queries, sorting descending by similarity and tie-breaking by document ID.

---

## 📋 Task Details

* **Input Data**: `q-cosine-similarity-server.json`
  * 250 technical documents (`D000001` through `D000250`), each with a 64-dim embedding vector.
  * 10 search queries (`Q001` through `Q010`), each with a 64-dim embedding vector.
* **Similarity Metric**:
  $$\text{Cosine Similarity} = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \times \|\mathbf{d}\|}$$
* **Tie-break Rule**:
  * If two documents have equal similarity, the smaller `doc_id` comes first (e.g. `D000001` before `D000002`).

---

## 🔑 Your Answer (JSON to Submit)

```json
{
  "Q001": [
    "D000111",
    "D000246",
    "D000176",
    "D000211",
    "D000241"
  ],
  "Q002": [
    "D000017",
    "D000227",
    "D000242",
    "D000152",
    "D000122"
  ],
  "Q003": [
    "D000203",
    "D000248",
    "D000018",
    "D000158",
    "D000058"
  ],
  "Q004": [
    "D000114",
    "D000129",
    "D000059",
    "D000179",
    "D000204"
  ],
  "Q005": [
    "D000200",
    "D000050",
    "D000005",
    "D000245",
    "D000220"
  ],
  "Q006": [
    "D000021",
    "D000016",
    "D000061",
    "D000056",
    "D000036"
  ],
  "Q007": [
    "D000117",
    "D000132",
    "D000002",
    "D000207",
    "D000197"
  ],
  "Q008": [
    "D000013",
    "D000153",
    "D000098",
    "D000183",
    "D000223"
  ],
  "Q009": [
    "D000039",
    "D000074",
    "D000129",
    "D000184",
    "D000009"
  ],
  "Q010": [
    "D000005",
    "D000220",
    "D000055",
    "D000050",
    "D000160"
  ]
}
```

---

## 🚀 How to Run

```bash
./q11/q11.sh
```
Or directly:
```bash
python3 q11/solution.py
```

