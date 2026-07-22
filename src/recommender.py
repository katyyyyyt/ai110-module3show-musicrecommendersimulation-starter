import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

# Columns in the CSV that hold numbers. Everything read from a CSV is a
# string, so we convert these ourselves. Anything not listed stays a string.
INTEGER_FIELDS = ["id"]
FLOAT_FIELDS = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file and returns a list of dictionaries,
    one dictionary per row (keys come from the CSV header).
    Required by src/main.py
    """
    songs = []

    # Open the file safely so it always closes when we are done.
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:

        # DictReader turns each row into a dict keyed by the header row.
        reader = csv.DictReader(f)

        for row in reader:
            # Convert whole-number columns with int().
            for field in INTEGER_FIELDS:
                # If a value is missing/empty, set it to None instead of crashing.
                try:
                    row[field] = int(row[field])
                except (ValueError, TypeError):
                    row[field] = None

            # Convert decimal columns with float().
            for field in FLOAT_FIELDS:
                try:
                    row[field] = float(row[field])
                except (ValueError, TypeError):
                    row[field] = None

            songs.append(row)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    return []

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []
