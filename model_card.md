# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeScout 1.0** — it scouts a small song catalog for the tunes that best match
your vibe.

---

## 2. Intended Use  

**Goal / task.** VibeScout takes a user's taste profile and suggests songs from
a fixed catalog. It predicts which songs a person is most likely to enjoy. It
ranks the whole catalog and returns the top 5. It also explains, in plain words,
why each song was picked.

**What it is for.** This is a classroom project for learning how recommenders
turn data into suggestions. It is meant for exploring and experimenting, not for
real listeners. It assumes the user can describe their taste as a genre, a mood,
a target energy level, and whether they like acoustic music.

**What it should not be used for.** It should not be used as a real music app or
to make decisions that matter to people. It only knows the 20 songs in its file.
It does not learn from listening history, and it does not understand lyrics,
culture, or context. Do not treat its picks as expert or personalized advice.

---

## 3. How the Model Works  

The model gives each song a score out of 100 points. It looks at four things and
adds up the points. Then it sorts the songs from highest to lowest score.

Here are the four rules (the baseline weights):

- **Mood — 35 points.** The song gets the full 35 if its mood matches yours. If
  not, it gets 0. Mood counts the most.
- **Genre — 30 points.** The song gets 30 if its genre matches yours. If not, 0.
- **Energy — up to 25 points.** This one is not all-or-nothing. The closer the
  song's energy is to your target, the more points it keeps. A perfect match
  gets almost all 25; a big gap gets very few.
- **Acoustic — 10 points.** Only counts if you said whether you like acoustic
  music. If the song matches your choice, it gets 10.

If two songs tie, the one with energy closer to your target wins. After that,
songs are ordered by title (A to Z).

I did run one experiment where I doubled the energy weight to 50 and halved the
genre weight to 15, just to see how much the ranking would move. The baseline
rules above are the main design.

---

## 4. Data  

The data is one small file called `songs.csv`. It has **20 songs**. Each song
has 10 columns.

Each song lists: an id, a title, an artist, a genre, a mood, and four number
features — energy, tempo (bpm), valence (how happy it sounds), danceability, and
acousticness. Right now the model only uses genre, mood, energy, and
acousticness. Tempo, valence, and danceability sit in the file but are not
scored.

The catalog is very mixed. There are about 15 genres, from pop and lofi to metal
and classical. Almost every song has a different mood. I used the starter data
as-is and did not add or remove songs.

Because the catalog is so small and spread out, most genres and moods appear
only once or twice. That means a lot of real tastes are missing. A user can also
ask for a mood or genre that simply is not in the file, and the model has no way
to fill that gap.

---

## 5. Strengths  

It works best for clear, mainstream tastes. If a user asks for a genre and mood
that exist in the catalog, the top pick is usually spot-on. For example, a
"happy pop" user gets "Sunrise City," which is exactly a happy pop song.

The energy dial also works well. Turn it up and the list fills with loud, fast
songs. Turn it down and the list turns calm and quiet. That matched my intuition
every time.

The best part is that every pick comes with a plain-language reason. You can
always see why a song was chosen, like "matches your happy mood" or "energy is
close to your target." Nothing is hidden. It never crashes on a normal profile,
and it gives a clean answer even when a user leaves fields blank.

---

## 6. Limitations and Bias 

The biggest weakness I found is that the **energy score gives partial credit to almost every song**, so a song can rank near the top without matching the user's genre or mood at all. Energy is scored as `points × (1 − |your energy − song energy|)`, which means any song whose energy is merely *close* to the target still earns most of those points. In my weight experiment (energy doubled to 50, genre halved to 15), "Velvet Groove" landed at #4 with a score of 50 for the `pop/happy` user **purely on energy proximity** — it is a funk/playful song that matches neither the requested genre nor mood. This exposes a bias toward middle-of-the-road energy values: because most songs in the catalog cluster between 0.28 and 0.97, a user with an average energy target (~0.5) is "close" to nearly everything and gets a smooth, undifferentiated list, while genre and mood — the things the user actually named — get drowned out. In short, the continuous energy signal makes the system reluctant to ever truly reject a song, which quietly undermines the exact preferences it is supposed to honor.

---

## 7. Evaluation  

I checked the recommender by hand-running a set of user profiles through it and
reading the top-5 lists, using the baseline weights (mood 35, genre 30, energy
25, acoustic 10). I deliberately included some "trick" profiles designed to
confuse the scorer. The profiles I tested were:

- **Happy Pop** — `genre=pop, mood=happy, energy=0.8` (the normal example user)
- **Sad but high-energy** — `genre=pop, mood=sad, energy=0.9` (conflicting taste)
- **Calm & acoustic** — `mood=chill, energy=0.95, likes_acoustic=True`
- **Impossible request** — `genre=polka, mood=triumphant, energy=0.5` (values not in the catalog)
- **Energy-only 0.5** vs **Energy-only 0.635** (two almost-identical dials)
- **Empty profile** — `{}` (no preferences at all)

**What surprised me most:** the system almost never says a firm "no." Because
energy always gives partial credit, even a profile that matched *nothing* on
genre or mood still produced a confident-looking ranked list. I also learned
that a preference the catalog doesn't contain (like the mood "sad") is silently
ignored — the user is asking for something real, but the scorer acts as if they
said nothing.

### Why "Gym Hero" keeps showing up for a "Happy Pop" user

Think of the scorer as a checklist, not a music critic. For the Happy Pop user,
"Gym Hero" ranked #3 because it ticked two of the boxes they asked for: it **is
pop** (so it earns the genre points) and its **energy (0.93) is close to the
requested 0.8** (so it earns most of the energy points). The one box it misses
is mood — "Gym Hero" is an *intense* workout track, not a *happy* one. But the
system has no way to know that an aggressive gym anthem feels wrong to someone
who wanted something cheerful; it only sees "pop ✓, high-energy ✓" and assumes
that is good enough. So the song keeps surfacing not because it's a mistake in
the code, but because the code is doing exactly what it was told — it just
wasn't told that mood matters more than raw energy to a happy listener.

### Profile comparisons (what changed, and why it makes sense)

- **Happy Pop vs. Sad-high-energy:** Happy Pop puts "Sunrise City" (pop/happy)
  on top, but flipping the mood to "sad" while raising energy to 0.9 pushes
  "Gym Hero" (pop/intense) to #1 instead. This makes sense: "sad" doesn't exist
  in the catalog, so that request is thrown away, and the high energy number
  then pulls the most intense songs to the top. The user asked for sad and got
  aggressive — a clear sign that a conflicting profile confuses the system.

- **Sad-high-energy vs. Calm & acoustic:** these are opposites, and the outputs
  are opposites too. The high-energy profile fills the top with loud, fast
  songs (rock, edm, k-pop), while the calm/acoustic profile shifts entirely to
  gentle low-energy tracks like "Midnight Coding" and "Library Rain" (lofi).
  This is the behavior working correctly — the energy dial really does move the
  list from "high-octane" to "quiet background music."

- **Energy-only 0.5 vs. Energy-only 0.635:** I expected a tiny change to barely
  matter, but nudging the energy target by about a tenth completely reshuffled
  the top 5 and changed which song was #1. This shows that when energy is the
  *only* thing scoring, the ranking becomes fragile and almost arbitrary —
  small input wiggles cause big output swings.

- **Impossible request vs. Empty profile:** asking for `polka / triumphant / 0.5`
  (none of which exist in the data) produced the **same** list as giving no
  preferences at all. This makes sense given how the code works — unmatched
  words score zero — but it's a real limitation: the system can't tell the
  difference between a picky user it failed and a user who said nothing.

Overall the outputs are *valid* in the sense that they follow the rules
faithfully, but the trick profiles show the rules don't always match human
intuition, especially when a stated preference isn't in the catalog.

---

## 8. Future Work  

If I kept building this, here are three things I would change:

1. **Give partial credit for close matches.** Right now "indie pop" earns zero
   against "pop." I would let similar genres and moods share some points, so
   near-misses are not treated as total strikes.

2. **Add a variety rule to the top 5.** The list can fill up with very similar
   songs. I would make sure the top picks include some range instead of three
   near-identical tracks.

3. **Use the features I am ignoring.** Tempo, valence, and danceability are just
   sitting in the file. I would score them too, so a user could ask for
   something like "danceable" or "upbeat" and actually get it.

---

## 9. Personal Reflection  

I learned that a recommender is really just a scoring rule plus a sort. There is
no magic. The system only knows what you tell it and what is in its data.

The most interesting thing was how much the weights matter. Small changes to the
points moved the results in big ways, and the system happily gave confident
answers even when the request made no sense to a human.

This changed how I see apps like Spotify. Now I think about what data they have,
what they choose to weigh, and what they might be leaving out. A recommendation
is a guess shaped by choices someone made — not a fact.

### Reflection on the engineering process

This was a pretty interesting project, and I really enjoyed working on it. This
time I decided to spend more time on every part instead of rushing. I kept
checking and modifying the code until I got the best result I could. I also
tested trick profiles and compared the outputs to make sure the system really
behaved the way I expected. Along the way I used AI as a tool to explain the
scoring math, catch edge cases, and try out changes quickly — and I think I used
it well, as a helper to understand and improve my work rather than to do it for
me.
