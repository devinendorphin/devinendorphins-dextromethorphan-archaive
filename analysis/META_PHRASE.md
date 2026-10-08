# META_PHRASE — "authoritarianism is interpersonal violence at scale"

*Measurements: `analysis/meta_phrase.py` (per-year theme densities per 10k
chars: power, coercion, institutions, intimate, scale vocabularies; weather
words as a disconfirming control). Reading: the theme-hit records, quoted
with local dates and URLs. All dates America/New_York.*

The user asked for three things: unpack the phrase, say how it maps onto the
analyst's language topology, and trace how it manifests in his posts across
time. In that order.

## 1. What the phrase might mean

"Authoritarianism is interpersonal violence at scale" makes a fractal claim.
It says the authoritarian and the abuser are not analogous — they are the
same operation running at different sizes. The strongman does to a population
what the coercive partner does to a partner: isolate, dominate the
information environment, punish exit, demand loyalty as the price of safety.
"At scale" does double work here. It means *magnitude* (many victims, a whole
polity) and it means *scale* in the infrastructure sense — the thing scales
because institutions, platforms, and bureaucracies are force-multipliers for
what one person could otherwise only do to the people in the room.

The phrase also reverses the usual direction of explanation. The standard
move is to explain the interpersonal by the structural (he hits because
patriarchy; she stays because the economy). This phrase explains the
structural by the interpersonal: the regime is legible if you have ever been
in the room with the person. That is a strong claim, and it has a tell: if it
is true, you should be able to watch a single writer move between the two
scales *without changing subject* — the political post and the dating post
should turn out to be the same post.

There is a weaker reading worth keeping on the table: that the phrase is a
moral heuristic, not a causal theory — a way of refusing to grade violence
on a curve by size. The corpus gets to adjudicate between the strong and
weak readings, because he spent eighteen years writing at both scales.

## 2. How it maps onto the analyst's language topology

Before this phrase, my sorting piles for the corpus were the obvious ones:
*political* posts (2025 strongman, ICE, reparations) and *personal* posts
(2021 hookups, the hall-of-mirrors series, DAAM). The phrase collapses the
piles. Once "interpersonal violence at scale" is the lens, the 2026-03-13
reel — "When it comes to the strongman personality, the Goldwater rule can
suck it. #badfaith #strongman #fascism #abuse"
(https://facebook.com/reel/3897039707093124/) — is not a political post with
an abuse hashtag; it is one post, about one thing, and the hashtag order
(#strongman #fascism #abuse) is the argument. The lens does not add
information; it removes a distinction I was imposing.

It also reorganizes the eras (`META_ERAS.md`). Era 4's DAAM series — "an
aggregate of every abuse narrative ever posted on quora, reddit… digested by
natural language processors into a single definitive abuse narrative"
(2021-10-03) — stops reading as "the domestic-abuse project" and starts
reading as *the scaling experiment*: interpersonal violence, literally run at
scale, through a language model. He was testing the phrase's machinery four
years before the phrase arrived, with the same tool (aggregation) the phrase
uses ("at scale").

The honest limit of the lens: it is a lens, and lenses find what they are
shaped to find (`LONGITUDINAL.md` §"What is not established": "The claim
vocabulary is a lens. It was written to catch one framing and will therefore
find it."). The weather-word control in `meta_phrase.py` exists for this
reason — and what it shows is that the theme densities do *not* track raw
volume noise (weather stays flat ~0.3–0.9/10k while the theme series move by
factors of 3–7×). The structure is in the writing, not the counting.

## 3. The theme across the eras, measured

Per-10k-character densities (from `meta_phrase.py`; n = records that year):

| year | power | coercion | institutions | intimate | scale | (weather) |
|---|---:|---:|---:|---:|---:|---:|
| 2008–2015 | 0.0–4.3 | 0.0 | 0.0–3.8 | 0.0 | 0.0 | 0.0–16.9 |
| 2016–2018 | 0.0 | 0.0 | 0.0–4.1 | 0.0–6.2 | 2.1–6.7 | 2.1–3.4 |
| 2019 | 1.1 | 0.9 | 1.1 | **3.1** | 2.5 | 0.5 |
| 2020 | 0.6 | 1.5 | **3.8** | 3.1 | 1.9 | 0.4 |
| 2021 | 0.6 | 1.2 | 2.2 | **5.2** | 1.7 | 0.8 |
| 2022 | 1.3 | 0.7 | 1.9 | 1.5 | 1.6 | 0.8 |
| 2023 | 1.1 | 0.8 | 2.8 | 2.4 | **3.0** | 0.5 |
| 2024 | 1.4 | 1.0 | 2.8 | 1.9 | 2.7 | 0.9 |
| 2025 | 1.3 | 0.9 | **4.0** | 2.1 | 2.4 | 0.3 |
| 2026 | **2.2** | 0.7 | 1.1 | 0.2 | **7.4** | 0.4 |

Three movements:

**The intimate arrives first (2019–2021).** The power vocabulary does not
precede the abuse vocabulary; it follows it. 2019: "Hi, my name is Devon, and
I don't know yet if I'm a survivor of narcissistic abuse" (2019-05-28) — and
in the same breath, skepticism of the frame: "Next post is gonna be about
dislike towards the construct of NPD Abuse as it has developed from 2014 to
present, cuz you know mental health language for the most part sucks."
(https://facebook.com/723125492/posts/pfbid0GtpRBJzmG2WmSzjbPY7zhmjjJ4SaQ88Z1eZh2RmxTLymtM5QV9hjp1HJqCpnuiTql/)
He uses the clinical language and distrusts it simultaneously — the first
sign that his theory of power will not be the therapeutic one.

2021 is the peak intimate year (5.2/10k) and it is a *production* year: DAAM
(daily abuse narratives, October), the smear-campaign spotter's guide
("1 - How to spot the inverts who start the smear campaigns.", 2021-06-25),
the hall-of-mirrors hookup post (2022-06-24). And the mechanism, stated in
the IIEA series:
> "As the abuser's self grows increasingly hopeless over time and realizes
> that they're powerless against the world and that all they've done
> throughout their lifetime was use everyone around them…"
> (2021-10-25, https://www.instagram.com/p/CVcjk5MgUmp/)

The abuser as *powerless* — violence as compensation for powerlessness. If
the phrase needs a mechanism, this is the one the corpus offers: domination
is what powerlessness does when it finds someone smaller.

**The institutional arrives with COVID and stays for Trump (2020, 2025).**
Institutions peak twice: 2020 (3.8 — "the NYPD… have access to an virtually
omniscient [Palantir system]", 2021-03-28,
https://facebook.com/723125492/posts/pfbid02mKnG7QUo7p3WQJRK48dLLVeKNJLi1uf9TxRQV7AAexasGbmKznWvJtWyVkR4rQ86l/)
and 2025 (4.0 — ICE, "the last Juneteenth", "reparations… braided in an ever
oscillating cycle of conqueror-enslaved", 2024-11-25,
https://facebook.com/723125492/posts/pfbid07MtTUSQvmNXSS8zSNBZBYDzFXk1ce2yuBCPiUtAMaWCFoNPufCc1beS9HKfdNCdWl/). The 2020–2021 bridge is the post that does
the phrase's work most explicitly:

> "This seems unrelated, but this is an attempt to show that the emotional
> responses due to the massacre, as media object, as itself a psychological
> operation, is by design… They will hide behind very sacred concepts to
> prevent being called out from the shady shit they do… **At the
> interpersonal level, it's like** this guy who tried to keep me at his home,
> even though I told him I needed to go."
> (2023-10-10,
> https://facebook.com/723125492/posts/pfbid0SC6euKWyPUdpSYmce42t719nBBB6UZSe3jCZqFNc9uR339bFT6tx5HGhWQ5yhL6sl/)

"At the interpersonal level, it's like" — the sentence *is* the phrase,
running in the other direction (macro → micro), three years before the
phrase was given to him. The strong reading survives this test: he moves
between scales without changing subject, in a single post, unprompted.

**The scale vocabulary detaches (2026).** Scale hits 7.4/10k while the
intimate vocabulary collapses to 0.2 — the only year they diverge that hard.
The subject is now systems: "system", "structural", "alignment". The
interpersonal hasn't disappeared; it has been *absorbed*. The 2026-03-13
strongman reel carries #abuse as a matter of course. The question the data
raises — and does not answer — is whether the absorption is insight (the
fractal seen whole) or loss (the room with the person, forgotten).

## 4. The mechanism, in his own words

The corpus offers three candidate mechanisms for how the small becomes the
large, and they are not the same:

1. **Compensation** (2021-10-25): the powerless dominate someone smaller.
   Bottom-up.
2. **Buy-in** (2024-03-31, "The Lord's Work"): the brutalized kid who
   "choos[es] instead to buy-in to the power embedded in white cops, and the
   resemblance of power over those white cops at the expense of the very
   youth he should be seeing himself in"
   (https://facebook.com/723125492/posts/pfbid0iMLe8cepf3MjBdjMcFDzKtVF6qK5UxoVvRJHGNwpXdwCwhfE3eaDoF2FerrybcEHl/).
   The victim becomes the enforcer. Lateral, then up.
3. **Paying it forward** (2022-08-09): "that doesn't give ya license to pay
   that shit forward to others via stigma." The cycle as such.

And the ironic inversion, which is also a theory (2022-06-24):

> "i wanna be your Lucy or Great Santini or the gymnastics coach that
> overexerts you to tears then hands you to the grabby doctor, cuz I have
> faith that this time I hurt you, you…"
> (https://facebook.com/723125492/posts/pfbid027xR8Qz97UKeG2WuwYyLahjBur3cjzEnD4LhkqL6dpjbKXoHfcgkAY4HxtVHmpJLl/)

Violence *as care*, performed in irony — the coach, the abuser, and the
healer in one figure. The corpus never resolves which of the three
mechanisms is primary. Neither does the phrase. That irresolution is honest:
the data supports the fractal (same shape at both scales) more firmly than
it supports any single direction of causation.

## 5. The disconfirming notes

- **2008–2018: the theme is absent.** Ten years, thousands of characters,
  weather outscores power. The phrase is not a constant of his writing; it is
  an arrival. Any reading that treats it as his perennial worldview is
  falsified by Era 1–2.
- **He distrusts the therapeutic frame** even while using it (2019-05-28:
  "mental health language for the most part sucks"). A reading that files him
  under "trauma discourse" misses the resistance, which is load-bearing.
- **2025-09-03**: "It's only fascism if you think it is. See how fucked up
  that sounds?"
  (https://www.instagram.com/p/DOJDSaTE80F/)
  — a warning, possibly to himself, against the lens becoming the finding.
  Kept here as the corpus's own caution label on this entire file.
- **The 2026 divergence** (scale 7.4, intimate 0.2) may be an artifact of the
  video-essay register: 49 of 61 FB posts in 2026 are videos, and only 17
  videos in the whole corpus carry transcripts. The intimate may have moved
  into speech. The corpus cannot say; the gap is stated in `META_EXPORT.md`.

## 6. One-paragraph read

The phrase is not imposed on the corpus; the corpus was already performing
it. From 2019 the intimate vocabulary arrives, from 2021 it becomes a
serialized project (DAAM), and on 2023-10-10 he writes the sentence the
phrase compresses — "At the interpersonal level, it's like…" — moving from a
massacre-as-psyop to a man who wouldn't let him leave a room, without
changing subject. What the phrase adds, as an analyst's lens, is the removal
of my own sorting piles: the strongman post and the dating post were never
two topics. What the corpus adds back, as a caution, is that he knew the
lens was a lens ("See how fucked up that sounds?"), distrusted the clinical
version of it, and by 2026 had scaled the vocabulary up so far that the room
with the person nearly drops out of the text. The fractal holds; the
direction of causation doesn't resolve; and the most honest sentence in the
file might be his, not mine: *it's only fascism if you think it is.*
