import requests
import time
import json
import os
from src.config import TMDB_API_KEY

HEADERS = {"Accept": "application/json"}
BASE_URL = "https://api.themoviedb.org/3/discover/"
SAVE_DIR = "data"
os.makedirs(SAVE_DIR, exist_ok=True)


def fetch_page(media_type, page):
	url = f"{BASE_URL}{media_type}"
	params = {
		"api_key": TMDB_API_KEY,
		"sort_by": "popularity.desc",
		"page": page,
		"vote_count.gte": 50,
		"language": "en-US"
	}
	response = requests.get(url, headers=HEADERS, params=params)

	if response.status_code == 429:
		retry_after = int(response.headers.get("Retry-After", 10))
		print(f"Rate limited. Waiting {retry_after} seconds...")
		time.sleep(retry_after)
		return fetch_page(media_type, page)

	if response.status_code != 200:
		print(f"Error fetching page {page} of {media_type}: {response.status_code}")
		return []

	return response.json().get("results", [])


def scrape_tmdb(media_type, max_pages=500, delay=0.25):
	output_path = os.path.join(SAVE_DIR, f"tmdb_{media_type}.jsonl")
	print(f"Saving {media_type} data to {output_path}")

	with open(output_path, "w", encoding="utf-8") as f:
		for page in range(1, max_pages + 1):
			print(f"Fetching {media_type} page {page}/{max_pages}")
			results = fetch_page(media_type, page)
			for entry in results:
				entry["media_type"] = media_type
				json.dump(entry, f)
				f.write("\n")
			time.sleep(delay)


if __name__ == "__main__":
	scrape_tmdb("movie")
	scrape_tmdb("tv")
