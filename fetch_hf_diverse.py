from datasets import load_dataset
import json
from pathlib import Path
import random
from collections import Counter


def generate_diverse_data():
    print("Loading HotpotQA from HuggingFace Datasets...")

    try:
        # Use train split to get easy / medium / hard diversity
        ds = load_dataset(
            "hotpotqa/hotpot_qa",
            "fullwiki",
            split="train"
        )
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    print(f"Total records: {len(ds)}")

    # Check real level distribution
    level_counter = Counter()
    type_counter = Counter()

    for item in ds:
        level_counter[item.get("level", "unknown")] += 1
        type_counter[item.get("type", "unknown")] += 1

    print("\nOriginal dataset distribution:")
    print("Difficulty:", dict(level_counter))
    print("Question Type:", dict(type_counter))

    # ---------------------------------------------------
    # Group by (difficulty, question_type)
    # Example:
    # easy_bridge
    # medium_comparison
    # hard_bridge
    # ---------------------------------------------------
    buckets = {}

    for item in ds:
        level = item.get("level", "hard")
        q_type = item.get("type", "bridge")

        key = f"{level}_{q_type}"

        if key not in buckets:
            buckets[key] = []

        buckets[key].append(item)

    print("\nBucket distribution:")
    for key, items in buckets.items():
        print(f"{key}: {len(items)}")

    # ---------------------------------------------------
    # Sample exactly 100 records with max diversity
    # ---------------------------------------------------
    random.seed(42)

    selected = []
    num_buckets = len(buckets)

    target_per_bucket = 100 // num_buckets
    remainder = 100 % num_buckets

    print(f"\nSampling strategy:")
    print(f"Buckets: {num_buckets}")
    print(f"Base per bucket: {target_per_bucket}")
    print(f"Remainder: {remainder}")

    for key, items in buckets.items():
        pool = items.copy()
        random.shuffle(pool)

        take_count = target_per_bucket

        if remainder > 0:
            take_count += 1
            remainder -= 1

        # prevent overflow if bucket too small
        take_count = min(take_count, len(pool))

        selected.extend(pool[:take_count])

    # ---------------------------------------------------
    # Fill remaining if < 100
    # ---------------------------------------------------
    if len(selected) < 100:
        print(f"\nOnly got {len(selected)} samples, filling remaining...")

        all_items = list(ds)
        random.shuffle(all_items)

        existing_ids = {x["id"] for x in selected}

        for item in all_items:
            if item["id"] not in existing_ids:
                selected.append(item)
                existing_ids.add(item["id"])

                if len(selected) == 100:
                    break

    # Final shuffle
    random.shuffle(selected)

    # ---------------------------------------------------
    # Format output
    # ---------------------------------------------------
    formatted_data = []

    for item in selected:
        contexts = []

        titles = item["context"]["title"]
        sentences_list = item["context"]["sentences"]

        for title, sentences in zip(titles, sentences_list):
            contexts.append({
                "title": title,
                "text": " ".join(sentences)
            })

        formatted_data.append({
            "qid": item["id"],
            "difficulty": item.get("level", "hard"),
            "type": item.get("type", "bridge"),
            "question": item["question"],
            "gold_answer": item["answer"],
            "context": contexts
        })

    # ---------------------------------------------------
    # Final stats check
    # ---------------------------------------------------
    final_diff_counter = Counter()
    final_type_counter = Counter()

    for item in formatted_data:
        final_diff_counter[item["difficulty"]] += 1
        final_type_counter[item["type"]] += 1

    print("\nFinal 100-sample distribution:")
    print("Difficulty:", dict(final_diff_counter))
    print("Question Type:", dict(final_type_counter))

    # ---------------------------------------------------
    # Save file
    # ---------------------------------------------------
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    out_path = out_dir / "hotpot_100_diverse.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully saved 100 diverse samples to:")
    print(out_path)


if __name__ == "__main__":
    generate_diverse_data()