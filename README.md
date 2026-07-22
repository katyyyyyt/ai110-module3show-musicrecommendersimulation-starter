# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

Real-world recommenders like Spotify and YouTube predict what you will love next by combining two big ideas: *collaborative filtering*, which looks at the behavior of millions of other users (likes, skips, plays, and shared playlists) to say "people with taste like yours also loved this," and *content-based filtering*, which looks at the attributes of the songs themselves (tempo, energy, mood, genre) to say "this sounds like what you already play." They blend these with context (time of day, device, activity) into large hybrid models. My version deliberately keeps it simple and focuses only on the content-based side: it scores each `Song` against a `UserProfile` using a handful of understandable features — genre and mood (exact matches), energy (rewarded by *closeness* to the user's preference, not by being high or low), and acousticness (rewarded when it matches whether the user likes acoustic music). I prioritize being **transparent and explainable** over being clever — every recommendation can be traced back to plain-language reasons ("recommended because it's lofi, chill, and matches your low-energy preference") rather than hidden math, so a reader can always see *why* a song was chosen.

Concretely, each `Song` carries nine attributes: `id`, `title`, and `artist` are used only for identification and display, while `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness` describe the music itself. My simple scorer actively uses just four of these — `genre` and `mood` (exact matches), `energy` (rewarded by closeness to preference), and `acousticness` (rewarded when it matches the user's `likes_acoustic` preference) — leaving `tempo_bpm`, `valence`, and `danceability` available for later experiments. The `UserProfile` stores four matching fields: `favorite_genre`, `favorite_mood`, `target_energy`, and `likes_acoustic`. These line up one-to-one with the song features (`favorite_genre` → `genre`, `favorite_mood` → `mood`, `target_energy` → `energy`, `likes_acoustic` → `acousticness`), which is exactly what makes each song easy to score and explain.

The data flows in three stages: **Input** is the `UserProfile` (favorite genre, favorite mood, target energy, and whether they like acoustic music); **Process** is the loop that judges every individual song loaded from `songs.csv` one at a time, passing each through my scoring logic to produce a point total plus a list of plain-language reasons; and **Output** is the ranking, where I sort all scored songs from highest to lowest and return the top *K* recommendations (default 5) so the user sees only the best matches rather than the whole catalog.

### Algorithm Recipe (finalized point weights)

Each song is scored out of **100 points** across four signals:

- **Mood match — 35 pts:** full points if the song's `mood` equals `favorite_mood`, else 0. Weighted highest because mood transfers across genres (a happy person wants happy songs regardless of style).
- **Genre match — 30 pts:** full points if `genre` equals `favorite_genre`, else 0. Kept just below mood on purpose — the catalog has ~15 genres across 20 songs, so over-weighting genre collapses the results to one or two songs.
- **Energy closeness — 25 pts:** continuous, `25 × (1 − |target_energy − energy|)`. Rewards near-misses and acts as the main tie-breaker among songs that don't match on genre.
- **Acoustic preference — 10 pts:** a softer lifestyle signal — rewards `acousticness ≥ 0.5` when `likes_acoustic` is true (and the reverse when false).

**Balance rationale:** a mood match (35) counts slightly more than a genre match (30), roughly 7:6, so neither categorical signal dominates alone (max 65), and the continuous energy/acoustic signals (35 combined) can still flip the ranking — which keeps the small, sparse catalog from producing a wall of ties.

### Potential biases I expect

- **Mood over genre:** because mood is weighted highest, the system may surface a "happy" metal track over a genuinely great rock song in the user's exact favorite genre — it can under-value strong genre matches that miss on mood.
- **Popularity of common values:** genres/moods that appear more often in the CSV have more chances to score points, so rare-genre songs are structurally disadvantaged regardless of quality.
- **Continuous-signal smoothing:** energy closeness gives partial credit to almost everything, so on a tiny catalog a song can rank high purely on being "near" the target energy while matching nothing the user actually named.
- **Ignored features:** `tempo_bpm`, `valence`, and `danceability` are unused, so two songs that feel very different to a listener but share genre/mood/energy are treated as interchangeable.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



