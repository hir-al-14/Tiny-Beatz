# convert_to_songs_csv.py
import pandas as pd
import os

RAW_PATH = "data/songs.csv"   # change to your actual raw CSV
OUT_PATH = "data/songs.csv"

if not os.path.exists(RAW_PATH):
    raise FileNotFoundError(
        f"{RAW_PATH} not found. Put your Kaggle CSV there or update RAW_PATH."
    )

# read with tolerant encoding
for enc in ["utf-8", "latin1", "ISO-8859-1", "cp1252"]:
    try:
        print(f"Trying encoding {enc}...")
        df = pd.read_csv(RAW_PATH, encoding=enc)
        print(f"Loaded with {enc}")
        break
    except Exception as e:
        print(f"Failed with {enc}: {e}")
else:
    raise RuntimeError("Could not read CSV with common encodings.")

print("Columns:", df.columns.tolist())

# Your dataset columns: playlist_url, year, track_id, track_name, track_popularity,
# album, artist_id, artist_name, artist_genres, artist_popularity, danceability,
# energy, key, loudness, mode, speechiness, acousticness, instrumentalness,
# liveness, valence, tempo, duration_ms, time_signature

# Keep all columns but add helpers so RAG knows where things are
df["artists"] = df["artist_name"].astype(str)
df["track_genre"] = df["artist_genres"].astype(str)
df["popularity"] = pd.to_numeric(df["track_popularity"], errors="coerce").fillna(0).astype(int)
df["valence"] = pd.to_numeric(df["valence"], errors="coerce")
df["energy"] = pd.to_numeric(df["energy"], errors="coerce")
df["danceability"] = pd.to_numeric(df["danceability"], errors="coerce")

# Drop rows missing song/artist
df = df.dropna(subset=["track_name", "artists"])

# Save full dataset (we'll filter/top-N inside RAG)
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
df.to_csv(OUT_PATH, index=False)
print(f"Saved cleaned songs dataset to {OUT_PATH} with {len(df)} rows.")
