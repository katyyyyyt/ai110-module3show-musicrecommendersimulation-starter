# load_songs.py
#
# This script reads a CSV file of songs and returns the data as a list of
# dictionaries (one dictionary per song). It uses ONLY Python's built-in
# tools — no pandas or other external libraries.
#
# Read it top-to-bottom: each step has a plain-English comment explaining
# what is happening and why.

# The "csv" module is part of Python's standard library. It knows how to
# read CSV files correctly (for example, handling commas inside quotes).
import csv


# We list here which columns hold NUMBERS instead of text.
# CSV files store EVERYTHING as text, so we must convert these ourselves.
#
# INTEGER_FIELDS are whole numbers  -> we convert them with int()
# FLOAT_FIELDS  are decimal numbers -> we convert them with float()
#
# Any column NOT listed here (like "title" or "artist") stays as a string.
INTEGER_FIELDS = ["id"]
FLOAT_FIELDS = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]


def load_songs(csv_path="data/songs.csv"):
    """
    Read the CSV file at csv_path and return a list of dictionaries.

    Each dictionary represents one row (one song). The dictionary keys are
    the column names taken from the header row of the CSV file.
    """

    # This list will collect one dictionary per song.
    songs = []

    # We open the file inside a "with" block. This guarantees the file is
    # automatically closed when we are done, even if an error happens.
    # newline="" is the recommended way to open files for the csv module.
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:

        # csv.DictReader reads the file and uses the first row (the header)
        # as the dictionary keys. Each following row becomes a dictionary
        # like {"id": "1", "title": "Sunrise City", ...}.
        reader = csv.DictReader(f)

        # Loop over every row in the file, one song at a time.
        for row in reader:

            # Convert the whole-number columns using int().
            for field in INTEGER_FIELDS:
                # We wrap the conversion in try/except so a missing or bad
                # value (like an empty string "") does NOT crash the program.
                # If the value cannot be converted, we store None instead,
                # which is Python's way of saying "no value here".
                try:
                    row[field] = int(row[field])
                except (ValueError, TypeError):
                    row[field] = None

            # Convert the decimal-number columns using float().
            for field in FLOAT_FIELDS:
                try:
                    row[field] = float(row[field])
                except (ValueError, TypeError):
                    # Same idea as above: keep going instead of crashing.
                    row[field] = None

            # Text columns (title, artist, genre, mood) are left untouched,
            # because they are already strings and should stay that way.

            # Add this finished song dictionary to our list.
            songs.append(row)

    # Give back the full list of song dictionaries to whoever called us.
    return songs


# This block only runs when you execute this file directly
# (for example: "python src/load_songs.py"). It will NOT run if another
# file imports load_songs. It is a quick way to check the function works.
if __name__ == "__main__":
    # Load all the songs from the default CSV location.
    all_songs = load_songs()

    # Show how many songs were loaded so we know something happened.
    print(f"Loaded {len(all_songs)} songs.")

    # Print the very first song so we can see the result and confirm that
    # the numeric fields are real numbers, not strings.
    if all_songs:
        print("First song:", all_songs[0])
