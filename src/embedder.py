from sentence_transformers import SentenceTransformer
import pandas as pd
import json
from .config import MOVIE_GENRES, TV_GENRES

model = SentenceTransformer('all-MiniLM-L6-v2')

def genre_list_to_names(genre_ids, media_type):
    if pd.isna(genre_ids):
        return ""
    ids = []
    if isinstance(genre_ids, str):
        try:
            ids = json.loads(genre_ids)
        except json.JSONDecodeError:
            return ""
    elif isinstance(genre_ids, list):
        ids = genre_ids
    else:
        return ""

    genre_map = MOVIE_GENRES if media_type == 'movie' else TV_GENRES
    return ", ".join(genre_map.get(gid, "") for gid in ids if gid in genre_map)

def add_embeddings(df):
    df = df[df['overview'].notnull()].copy()
    df['genres'] = df.apply(lambda row: genre_list_to_names(row['genre_ids'], row['media_type']), axis=1)
    df['combined_text'] = df['overview'] + ". Genres: " + df['genres']
    df['embedding'] = df['combined_text'].apply(lambda x: model.encode(x).tolist())
    return df