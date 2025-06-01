import csv
import json
import requests
from pathlib import Path
from src.config import METADATA_PATH

DATA_DIR = Path("data")
IMAGE_DIR = DATA_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

TMDB_FIELDS = [
    "id", "title", "original_title", "overview", "release_date", "genre_ids",
    "original_language", "popularity", "vote_average", "vote_count",
    "poster_path", "backdrop_path", "adult", "video", "media_type"
]

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def download_image(image_path):
    if not image_path:
        return ""
    filename = IMAGE_DIR / image_path.strip("/")
    if filename.exists():
        return str(filename.relative_to(DATA_DIR))
    url = f"{TMDB_IMAGE_BASE}{image_path}"
    print(f"Downloading {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return ""
    return str(filename.relative_to(DATA_DIR))

def unify_items(*item_lists):
    merged = {}
    for items in item_lists:
        for item in items:
            title = item.get("title") or item.get("name")
            media_type = item.get("media_type")
            if not title or not media_type:
                print(f"Skipping invalid item: {item}")
                continue

            # Normalize fields for TV shows
            item["title"] = item.get("title") or item.get("name")
            item["original_title"] = item.get("original_title") or item.get("original_name")
            item["release_date"] = item.get("release_date") or item.get("first_air_date")

            # Download and replace image paths
            item["poster_path"] = download_image(item.get("poster_path"))
            item["backdrop_path"] = download_image(item.get("backdrop_path"))

            key = (title.lower(), media_type)
            if key not in merged or count_non_empty_fields(item) > count_non_empty_fields(merged[key]):
                merged[key] = item
    return list(merged.values())

def count_non_empty_fields(item):
    return sum(1 for field in TMDB_FIELDS if item.get(field))

def save_merged_csv(items, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TMDB_FIELDS)
        writer.writeheader()
        for item in items:
            row = item.copy()
            row["genre_ids"] = json.dumps(item.get("genre_ids", []))
            row = {k: v for k, v in row.items() if k in TMDB_FIELDS}
            writer.writerow(row)

def main():
    print("Loading datasets...")
    scraped_movies = load_jsonl(DATA_DIR / "tmdb_movie.jsonl")
    scraped_tv = load_jsonl(DATA_DIR / "tmdb_tv.jsonl")

    print("Merging datasets...")
    all_items = unify_items(scraped_movies, scraped_tv)

    print(f"Saving {len(all_items)} merged items...")
    save_merged_csv(all_items, METADATA_PATH)
    print("Done.")

if __name__ == "__main__":
    main()
