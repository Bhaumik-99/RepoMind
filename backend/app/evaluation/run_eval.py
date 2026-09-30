from ..rag.store import RepoIndex

GOLD = [
    # {"repo_id": "...", "question": "Where is the auth middleware?", "expected_paths": ["src/auth.py"]},
]

def evaluate():
    if not GOLD:
        print("Add gold questions in backend/app/evaluation/run_eval.py before running evaluation.")
        return
    hits = 0
    total = len(GOLD)
    for row in GOLD:
        results = RepoIndex(row["repo_id"]).search(row["question"], 5)
        paths = {r["path"] for r in results}
        hits += int(bool(paths.intersection(row["expected_paths"])))
    print(f"Recall@5: {hits/total:.3f}")

if __name__ == "__main__":
    evaluate()
