import os
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from config import DATA_CSV_PATH, EMB_PATH, EMBED_MODEL


@dataclass
class SongResult:
    track_name: str
    artists: str
    genre: str
    popularity: int
    score: float


class SongRAG:
    """
    Simple RAG over the Kaggle Top Hits dataset.

    - Load the full CSV.
    - Create helper columns (artists, track_genre, popularity, valence, energy).
    - Build a natural-language "vibe" description for each song and embed it.
    - At query time, embed the user text and retrieve nearest songs by cosine similarity + a popularity.
    """

    def __init__(self):
        # Load full dataset
        self.df = self._load_data()

        # Load embedding model
        self.model = SentenceTransformer(EMBED_MODEL)

        # Load or build embeddings
        self.embeddings = self._load_or_build_embeddings()

    # data
    def _load_data(self) -> pd.DataFrame:
        df = pd.read_csv(DATA_CSV_PATH, encoding="latin1")

        # Helper columns
        df["artists"] = df["artist_name"].astype(str)
        df["track_genre"] = df["artist_genres"].astype(str)
        df["popularity"] = (
            pd.to_numeric(df["track_popularity"], errors="coerce")
            .fillna(0)
            .astype(int)
        )
        df["valence"] = pd.to_numeric(df["valence"], errors="coerce").fillna(0.5)
        df["energy"] = pd.to_numeric(df["energy"], errors="coerce").fillna(0.5)

        # Drop rows missing key info
        df = df.dropna(subset=["track_name", "artists"])

        # Sort by popularity
        df = df.sort_values("popularity", ascending=False).reset_index(drop=True)
        return df

    def _vibe_text(self, row) -> str:
        """Build a simple natural language description for each track."""
        name = str(row["track_name"])
        artists = str(row["artists"])
        year = str(row.get("year", ""))
        genres = str(row.get("track_genre", ""))

        val = float(row.get("valence", 0.5))
        energy = float(row.get("energy", 0.5))
        dance = float(row.get("danceability", 0.5))

        # Map numbers → words
        if val > 0.7:
            val_txt = "very happy and positive"
        elif val > 0.5:
            val_txt = "warm and somewhat positive"
        elif val > 0.4:
            val_txt = "neutral"
        else:
            val_txt = "sad and emotional"

        if energy > 0.7:
            energy_txt = "high energy and upbeat"
        elif energy > 0.4:
            energy_txt = "medium energy and groovy"
        else:
            energy_txt = "low energy and calm"

        if dance > 0.6:
            dance_txt = "very danceable"
        elif dance > 0.4:
            dance_txt = "a bit danceable"
        else:
            dance_txt = "not very danceable"

        return (
            f"Song {name} by {artists} from year {year}. "
            f"Genres: {genres}. "
            f"Vibe: {val_txt}, {energy_txt}, {dance_txt}."
        )

    def _build_corpus(self):
        texts = []
        for _, row in self.df.iterrows():
            texts.append(self._vibe_text(row))
        return texts

    # embeddings

    def _load_or_build_embeddings(self) -> np.ndarray:
        # Normal path: if file exists, use it
        if os.path.exists(EMB_PATH):
            data = np.load(EMB_PATH, allow_pickle=True)
            return data["embeddings"]

        # Otherwise build and save
        corpus = self._build_corpus()
        embeddings = self.model.encode(
            corpus,
            batch_size=64,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        os.makedirs(os.path.dirname(EMB_PATH), exist_ok=True)
        np.savez(EMB_PATH, embeddings=embeddings)
        return embeddings

    # retrieval

    def retrieve(self, query: str, k: int = 5, popularity_weight: float = 0.3) -> List[SongResult]:
        """Embed query, compute similarity, add popularity bonus, return top-k songs."""
        if not query:
            return []

        q_emb = self.model.encode([query], normalize_embeddings=True)[0]
        sims = self.embeddings @ q_emb  # cosine similarity (vectors normalized)

        pop = self.df["popularity"].values.astype(float)
        pop_norm = (pop - pop.min()) / (pop.max() - pop.min() + 1e-8)

        scores = sims + popularity_weight * pop_norm
        top_idx = np.argsort(-scores)[:k]

        results: List[SongResult] = []
        for idx in top_idx:
            row = self.df.iloc[idx]
            results.append(
                SongResult(
                    track_name=str(row["track_name"]),
                    artists=str(row["artists"]),
                    genre=str(row.get("track_genre", "")),
                    popularity=int(row["popularity"]),
                    score=float(scores[idx]),
                )
            )
        return results

if __name__ == "__main__":
    print("Rebuilding TinyBeatz embeddings from scratch…")

    if os.path.exists(EMB_PATH):
        os.remove(EMB_PATH)
        print(f"Existing embedding file removed: {EMB_PATH}")

    rag = SongRAG()
    print(f"Done. Embedded {len(rag.df)} songs → {EMB_PATH}")
