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

Below is real terminal output from running `python -m src.main` with the
example profile `genre=pop, mood=happy, energy=0.8`:

```
====================================================
                  MUSIC RECOMMENDER
====================================================
  Loaded 20 songs from the catalog
  Your taste: genre=pop, mood=happy, energy=0.8
====================================================

  Top 5 recommendations for you:

  1. Sunrise City  -  Neon Echo
     Score:  89.50 / 100
     Why:
       - matches your happy mood (+35)
       - matches your favorite genre pop (+30)
       - energy is close to your target (+24.5)

  2. Rooftop Lights  -  Indigo Parade
     Score:  59.00 / 100
     Why:
       - matches your happy mood (+35)
       - energy is close to your target (+24.0)

  3. Gym Hero  -  Max Pulse
     Score:  51.75 / 100
     Why:
       - matches your favorite genre pop (+30)
       - energy is close to your target (+21.8)

  4. Velvet Groove  -  The Slick Six
     Score:  25.00 / 100
     Why:
       - energy is close to your target (+25.0)

  5. Night Drive Loop  -  Neon Echo
     Score:  23.75 / 100
     Why:
       - energy is close to your target (+23.8)
```

---

## Adversarial / Edge-Case Testing

To stress-test the scoring logic, I ran ten "adversarial" profiles designed to
trick the scorer or expose unexpected behavior. Each block below is real
terminal output showing the top 5 (`score  title  (genre/mood, energy)`).

**1a. Conflicting mood vs. energy** — asks for a `sad` mood (which no song has)
at high energy `0.9`. Mood scores 0 for everyone, so energy quietly drives the
list toward aggressive tracks:

```
1a. conflicting: pop/sad/0.9
  prefs = {'genre': 'pop', 'mood': 'sad', 'energy': 0.9}
------------------------------------------------------------
  1.  54.25  Gym Hero               (pop/intense, e=0.93)
  2.  53.00  Sunrise City           (pop/happy, e=0.82)
  3.  24.75  Storm Runner           (rock/intense, e=0.91)
  4.  24.00  Red Red                (k-pop/energetic, e=0.86)
  5.  23.75  Neon Overdrive         (edm/euphoric, e=0.95)
```

**1b. Physically incompatible preferences** — `chill` + acoustic + high energy
`0.95` can't all be satisfied (chill/acoustic songs are all low-energy). Mood
(35) + acoustic (10) outweigh energy (25), so the loud energy preference loses:

```
1b. incompatible: chill/0.95/acoustic
  prefs = {'mood': 'chill', 'energy': 0.95, 'likes_acoustic': True}
------------------------------------------------------------
  1.  56.75  Midnight Coding        (lofi/chill, e=0.42)
  2.  55.00  Library Rain           (lofi/chill, e=0.35)
  3.  53.25  Spacewalk Thoughts     (ambient/chill, e=0.28)
  4.  25.75  Dust and Diesel        (country/nostalgic, e=0.58)
  5.  25.00  Neon Overdrive         (edm/euphoric, e=0.95)
```

**2. Values that don't exist in the catalog** — unmatched genre/mood contribute
nothing, so the result is identical to profile 3a (energy-only). The system
can't tell a specific-but-impossible request from a blank one:

```
2.  nonexistent: polka/triumphant/0.5
  prefs = {'genre': 'polka', 'mood': 'triumphant', 'energy': 0.5}
------------------------------------------------------------
  1.  24.50  A Boy                  (k-pop/dreamy, e=0.52)
  2.  24.50  Slow Burn Letters      (r&b/romantic, e=0.48)
  3.  23.75  Island Time            (reggae/laidback, e=0.55)
  4.  23.00  Dust and Diesel        (country/nostalgic, e=0.58)
  5.  23.00  Midnight Coding        (lofi/chill, e=0.42)
```

**3a. Energy-only, midpoint 0.5** — with no genre/mood, everything scores only
on energy closeness and ties are broken by energy gap, then title:

```
3a. energy only 0.5
  prefs = {'energy': 0.5}
------------------------------------------------------------
  1.  24.50  A Boy                  (k-pop/dreamy, e=0.52)
  2.  24.50  Slow Burn Letters      (r&b/romantic, e=0.48)
  3.  23.75  Island Time            (reggae/laidback, e=0.55)
  4.  23.00  Dust and Diesel        (country/nostalgic, e=0.58)
  5.  23.00  Midnight Coding        (lofi/chill, e=0.42)
```

**3b. Energy-only, 0.635** — a tiny input change (0.5 → 0.635) completely
reshuffles the ranking and flips the leader, showing how fragile the ordering
is when energy is the only active signal:

```
3b. energy only 0.635
  prefs = {'energy': 0.635}
------------------------------------------------------------
  1.  23.62  Dust and Diesel        (country/nostalgic, e=0.58)
  2.  22.88  Island Time            (reggae/laidback, e=0.55)
  3.  22.38  Concrete Kings         (hip-hop/confident, e=0.74)
  4.  22.12  A Boy                  (k-pop/dreamy, e=0.52)
  5.  22.12  Night Drive Loop       (synthwave/moody, e=0.75)
```

**4a. Out-of-range energy 5.0** — the energy term goes negative and is clamped
to 0 for *every* song, so the whole energy signal is silently zeroed and only
genre points survive (no warning):

```
4a. out-of-range energy 5.0
  prefs = {'genre': 'pop', 'energy': 5.0}
------------------------------------------------------------
  1.  30.00  Gym Hero               (pop/intense, e=0.93)
  2.  30.00  Sunrise City           (pop/happy, e=0.82)
  3.   0.00  Iron Verdict           (metal/aggressive, e=0.97)
  4.   0.00  Neon Overdrive         (edm/euphoric, e=0.95)
  5.   0.00  Storm Runner           (rock/intense, e=0.91)
```

**4b. Wrong-type energy `"high"`** — a non-numeric energy value crashes the run.
The guard checks for `None` but not for a numeric type (**confirmed bug**):

```
4b. wrong-type energy 'high'
  prefs = {'genre': 'pop', 'energy': 'high'}
------------------------------------------------------------
  !!! CRASHED: TypeError: unsupported operand type(s) for -: 'str' and 'float'
```

**5a. Whitespace / case normalization** — `"  POP "` and `"HAPPY"` still match
correctly, confirming the scorer trims and lowercases text (good control):

```
5a. whitespace/case '  POP '/'HAPPY'
  prefs = {'genre': '  POP ', 'mood': 'HAPPY'}
------------------------------------------------------------
  1.  65.00  Sunrise City           (pop/happy, e=0.82)
  2.  35.00  Rooftop Lights         (indie pop/happy, e=0.76)
  3.  30.00  Gym Hero               (pop/intense, e=0.93)
  4.   0.00  A Boy                  (k-pop/dreamy, e=0.52)
  5.   0.00  Coffee Shop Stories    (jazz/relaxed, e=0.37)
```

**5b. `likes_acoustic` as the string `"yes"`** — the acoustic points never award
because a string is compared to a boolean, so the opted-in user gets the same
all-zero result as an empty profile (**confirmed bug**):

```
5b. likes_acoustic 'yes' (string)
  prefs = {'likes_acoustic': 'yes'}
------------------------------------------------------------
  1.   0.00  A Boy                  (k-pop/dreamy, e=0.52)
  2.   0.00  Coffee Shop Stories    (jazz/relaxed, e=0.37)
  3.   0.00  Concrete Kings         (hip-hop/confident, e=0.74)
  4.   0.00  Dust and Diesel        (country/nostalgic, e=0.58)
  5.   0.00  Focus Flow             (lofi/focused, e=0.4)
```

**6. Empty profile** — no preferences at all: every song scores 0 and the list
falls back to alphabetical-by-title without crashing (graceful degradation):

```
6.  empty profile
  prefs = {}
------------------------------------------------------------
  1.   0.00  A Boy                  (k-pop/dreamy, e=0.52)
  2.   0.00  Coffee Shop Stories    (jazz/relaxed, e=0.37)
  3.   0.00  Concrete Kings         (hip-hop/confident, e=0.74)
  4.   0.00  Dust and Diesel        (country/nostalgic, e=0.58)
  5.   0.00  Focus Flow             (lofi/focused, e=0.4)
```

**Takeaways:** three profiles exposed genuine defects — `energy: "high"` crashes
(4b), `likes_acoustic: "yes"` is silently ignored (5b), and an out-of-range
energy silently zeroes the energy signal (4a). The rest produce valid but
sometimes counter-intuitive rankings when a stated preference matches nothing.

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



