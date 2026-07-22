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

# Scoring weights from the README "Algorithm Recipe" (100 points total).
# Defined once at module level so they are not rebuilt on every score_song()
# call, and so they live in one obvious place if you want to tune them.
MOOD_POINTS = 35
GENRE_POINTS = 30
ENERGY_POINTS = 25
ACOUSTIC_POINTS = 10

# A song counts as "acoustic" at or above this acousticness value.
ACOUSTIC_THRESHOLD = 0.5


def _same_text(a, b) -> bool:
    """
    Compare two text values fairly: ignore surrounding spaces and letter
    case, so "Pop", "pop ", and "pop" all count as the same thing.
    Returns False if either value is missing.
    """
    if a is None or b is None:
        return False
    return str(a).strip().lower() == str(b).strip().lower()


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
    Scores a single song against the user's preferences.

    This follows the "Algorithm Recipe" from the README: each song is scored
    out of 100 points across four signals.
        - Mood match ........ 35 points (exact match)
        - Genre match ....... 30 points (exact match)
        - Energy closeness .. 25 points (closer to target = more points)
        - Acoustic pref ..... 10 points (matches likes_acoustic)

    Returns a tuple: (total_score, reasons) where reasons is a list of short
    plain-language strings explaining where the points came from.
    """
    # The user's preferences can arrive with different key names, so we look
    # up both the README style ("favorite_genre") and the main.py style
    # ("genre"). If neither is present we get None and simply skip that signal.
    favorite_genre = user_prefs.get("favorite_genre", user_prefs.get("genre"))
    favorite_mood = user_prefs.get("favorite_mood", user_prefs.get("mood"))
    target_energy = user_prefs.get("target_energy", user_prefs.get("energy"))
    likes_acoustic = user_prefs.get("likes_acoustic")  # may be None if unset

    # We build up the score and a list of reasons as we go.
    score = 0.0
    reasons: List[str] = []

    # --- Mood match (35 points) -------------------------------------------
    # Full points only when the song's mood equals the user's mood
    # (ignoring case and spacing, so "Happy" still matches "happy").
    if _same_text(song.get("mood"), favorite_mood):
        score += MOOD_POINTS
        reasons.append(f"matches your {favorite_mood} mood (+{MOOD_POINTS})")

    # --- Genre match (30 points) ------------------------------------------
    # Kept just below mood so genre does not dominate on a small catalog.
    if _same_text(song.get("genre"), favorite_genre):
        score += GENRE_POINTS
        reasons.append(f"is {favorite_genre}, your favorite genre (+{GENRE_POINTS})")

    # --- Energy closeness (up to 25 points) -------------------------------
    # This is a continuous score: the closer the song's energy is to the
    # user's target, the more points it earns. Formula: 25 * (1 - |diff|).
    song_energy = song.get("energy")
    if target_energy is not None and isinstance(song_energy, (int, float)):
        # Energy values live on a 0.0 - 1.0 scale, so the gap is 0.0 - 1.0 too.
        difference = abs(target_energy - song_energy)
        # max(0, ...) keeps the score from ever going negative when the
        # values are far apart, in one clear step.
        energy_score = max(0, ENERGY_POINTS * (1 - difference))
        score += energy_score
        reasons.append(f"energy is close to your target (+{energy_score:.1f})")

    # --- Acoustic preference (10 points) ----------------------------------
    # A softer "lifestyle" signal. Only applies if the user stated a
    # preference. A song counts as acoustic when acousticness >= 0.5.
    acousticness = song.get("acousticness")
    if likes_acoustic is not None and isinstance(acousticness, (int, float)):
        song_is_acoustic = acousticness >= ACOUSTIC_THRESHOLD
        # Award points when the song's acoustic-ness matches the preference
        # (acoustic song for someone who likes acoustic, or vice versa).
        if song_is_acoustic == likes_acoustic:
            score += ACOUSTIC_POINTS
            label = "acoustic" if likes_acoustic else "non-acoustic"
            reasons.append(f"is {label}, matching your taste (+{ACOUSTIC_POINTS})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # Score every song one at a time and collect (song, score, explanation).
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)

        # Turn the list of reasons into one readable sentence. If a song
        # matched nothing, give a friendly fallback message instead.
        if reasons:
            explanation = "Recommended because it " + ", ".join(reasons)
        else:
            explanation = "No strong matches, but here it is anyway"

        scored.append((song, score, explanation))

    # Sort from highest score to lowest so the best matches come first.
    # key=lambda item: item[1] means "sort by the score (the 2nd item)".
    scored.sort(key=lambda item: item[1], reverse=True)

    # Return only the top k results so the user sees the best matches.
    return scored[:k]
