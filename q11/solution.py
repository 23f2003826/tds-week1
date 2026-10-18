import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "q-cosine-similarity-server.json"
OUTPUT_PATH = BASE_DIR / "solution.json"

def compute_top5_cosine():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = data["documents"]
    queries = data["queries"]

    results = {}

    for q in queries:
        qid = q["query_id"]
        q_emb = q["embedding"]

        scored_docs = []
        for d in documents:
            did = d["doc_id"]
            d_emb = d["embedding"]

            # Compute dot product and norms for exact cosine similarity
            dot = sum(x * y for x, y in zip(q_emb, d_emb))
            norm_q = math.sqrt(sum(x * x for x in q_emb))
            norm_d = math.sqrt(sum(x * x for x in d_emb))

            sim = dot / (norm_q * norm_d) if (norm_q > 0 and norm_d > 0) else 0.0
            scored_docs.append((sim, did))

        # Tie-break rule: Sort similarity descending (-item[0]), then doc_id ascending (item[1])
        scored_docs.sort(key=lambda item: (-item[0], item[1]))

        # Take top 5
        top5 = [did for sim, did in scored_docs[:5]]
        results[qid] = top5

    # Save to solution.json
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    res = compute_top5_cosine()
    print(json.dumps(res, indent=2))

