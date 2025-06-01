import pandas as pd
import json
from src.embedder import add_embeddings
from src.config import METADATA_PATH

print("Loading metadata...")
df = pd.read_csv(METADATA_PATH)

print("Generating embeddings...")
df = add_embeddings(df)

print("Saving updated metadata...")
df['embedding'] = df['embedding'].apply(json.dumps)
df.to_csv(METADATA_PATH, index=False)

print("Done. Embeddings refreshed and saved.")