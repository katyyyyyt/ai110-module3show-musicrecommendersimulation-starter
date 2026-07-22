"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


# The explanation string from the recommender looks like:
#   "Recommended because it is pop (+30), matches your happy mood (+35)"
# This prefix is shared by every explanation, so we strip it off before
# splitting the sentence back into its individual reasons.
REASON_PREFIX = "Recommended because it "


def explanation_to_reasons(explanation: str):
    """
    Split one explanation sentence back into its separate reason phrases so
    we can show them as a clean bulleted list. Returns a list of strings.
    """
    # Remove the shared prefix if it is there.
    if explanation.startswith(REASON_PREFIX):
        explanation = explanation[len(REASON_PREFIX):]
    # The scorer joined the reasons with ", ", so we split on that.
    return [reason.strip() for reason in explanation.split(",")]


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # --- Header: show what we loaded and who we are recommending for ------
    print()
    print("=" * 52)
    print("  MUSIC RECOMMENDER".center(52))
    print("=" * 52)
    print(f"  Loaded {len(songs)} songs from the catalog")
    print(
        "  Your taste: "
        f"genre={user_prefs['genre']}, "
        f"mood={user_prefs['mood']}, "
        f"energy={user_prefs['energy']}"
    )
    print("=" * 52)
    print(f"\n  Top {len(recommendations)} recommendations for you:\n")

    # --- Body: one clean, numbered block per recommended song ------------
    # enumerate(..., start=1) gives us a human-friendly rank (1, 2, 3, ...).
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        # Title line: rank, song title, and the artist for context.
        print(f"  {rank}. {song['title']}  -  {song['artist']}")
        # Score line, padded so the numbers line up neatly.
        print(f"     Score: {score:6.2f} / 100")
        # Reasons, one per line as a bulleted list.
        print("     Why:")
        for reason in explanation_to_reasons(explanation):
            print(f"       - {reason}")
        # Blank line between songs so each block is easy to read.
        print()


if __name__ == "__main__":
    main()
