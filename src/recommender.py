from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import ast
import pandas as pd
from src.config import METADATA_PATH

_cached_df = None

def get_cached_dataset():
    global _cached_df
    if _cached_df is None:
        import ast
        df = pd.read_csv(METADATA_PATH)
        df = df[df['embedding'].notnull()].reset_index(drop=True)
        df['embedding'] = df['embedding'].apply(lambda x: np.array(ast.literal_eval(x)) if isinstance(x, str) else x)
        _cached_df = df
    return _cached_df

def get_recommendations(df, title, top_n=15):
    embeddings = np.vstack(df['embedding'].values)
    similarity_matrix = cosine_similarity(embeddings)

    match = df[df['title'].str.lower().str.contains(title.lower())]
    if match.empty:
        return []

    idx = match.index[0]
    query_title = title.lower()
    query_genres = set(json.loads(df.iloc[idx]['genre_ids']) if isinstance(df.iloc[idx]['genre_ids'], str) else df.iloc[idx]['genre_ids'])

    scores = []
    for i in range(len(df)):
        if i == idx:
            continue

        candidate_title = df.iloc[i]['title'].lower()
        candidate_genres = set(json.loads(df.iloc[i]['genre_ids']) if isinstance(df.iloc[i]['genre_ids'], str) else df.iloc[i]['genre_ids'])

        genre_score = len(query_genres & candidate_genres) / len(query_genres | candidate_genres) if query_genres | candidate_genres else 0.0
        similarity_score = similarity_matrix[idx][i]
        combined_score = 0.8 * similarity_score + 0.2 * genre_score

        scores.append((i, combined_score))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # Filter out any title that contains the query title or vice versa
    filtered = []
    for i, _ in scores:
        candidate_title = df.iloc[i]['title'].lower()
        if query_title in candidate_title or candidate_title in query_title:
            continue
        filtered.append(df.iloc[i]['title'])
        if len(filtered) == top_n:
            break

    return filtered
