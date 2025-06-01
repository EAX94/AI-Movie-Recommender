import argparse
import pandas as pd
import json
from .config import METADATA_PATH
from .recommender import get_recommendations

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', type=str, required=True)
    args = parser.parse_args()

    df = pd.read_csv(METADATA_PATH)
    df['embedding'] = df['embedding'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)

    recs = get_recommendations(df, args.title)
    print(f"Recommendations for {args.title}:")
    for r in recs:
        print(f"- {r}")

if __name__ == "__main__":
    run()