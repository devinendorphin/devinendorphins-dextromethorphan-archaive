# META_RESIDENCES — residence history mapped to life areas

*Candidates: `analysis/meta_residences.py` (broad recall), then targeted
greps and manual curation. Every dated claim below is quoted with its post;
uncertainty is stated where it exists. All dates America/New_York.*

The corpus is thin on addresses — he almost never names a street or a
building — but it is rich on *moves*, and on the philosophy of residence
itself. The timeline:

## The dated timeline

**Downey, California — childhood/adolescence.** `profile_info.json` lists
"Downey High" under education and the birthdate 1985-12-22. No post in the
corpus describes growing up there; this is the only record of it. Note the
tension: the same profile lists hometown as "Brooklyn, New York" — verbatim
from the API, and irreconcilable with Downey High except as aspiration,
re-identification, or a field filled in later. The writeup does not resolve
it; both values are kept.

**Los Angeles, ~2000–~2002.** "Hello Queer Imaginary… We're in Los Angeles
twenty years ago. We're attending the opening of the ONE Archives."
(2020-06-04,
https://facebook.com/723125492/posts/pfbid0JdBZQoEkGkEVGdRSjpXgjhMCMbGRCryPoMRrXp67x5ExfTTjh99KdQB7UQmAXCPnl/).
USC is also in the education list; the corpus never
says whether the LA years were the USC years. **Uncertain.**

**New York City, ~2002 → present.** "Oh, shit. I have been in NYC for 20
years!" (2022-08-25,
https://facebook.com/723125492/posts/pfbid02BrTmNnK2RUquUrw768r95eFSPvqHdaq7YrX8FcYiyoMpigxAR7mRB2mGMyC6cyE4l/).
Twenty years back from August 2022 is ~2002. Columbia University is in the
education list, undated.

**An apartment, by 2010.** "they say they start paying me the moment I leave
my apartment to head to the session" (2010-04-19 — the Masonic Temple
fingerprinting post). No neighborhood named. **Uncertain which.**

**"Two or more homes," 2010s.** In the 2021-07-23 video he looks back:
"For years, I've always had two or more homes I could lay my head at… Cuz my
home is actually in my backpack most times." (video transcript,
https://facebook.com/devon.gallegos/videos/982696215840942/). This is not a
list of addresses; it is a residence *philosophy* — polyamory applied to
shelter — and it explains why the corpus yields so few fixed locations.

**Brooklyn, by 2021.** "Robert L. Williams bursts into your Brooklyn home"
(2021-05-05, IG). Profile `current_city`: "Brooklyn, New York" (retrieved
2026-10-07). No earlier post names Brooklyn as his residence; the 2014
earthquake post ("19th floor of a building built in the 19th century, on the
wrong coast, at the office") places him *at work*, not at home.

**A move and a homelessness scare, January 2025.** "Having a party the last
weekend of my move? The last set days I have to focus on packing before being
homeless? Mayor Adams Logic." (2025-01-25,
https://facebook.com/723125492/posts/pfbid02uFzVpDHyRxt5xEiH5f93Ae4fWDxhsVGiFZD94mZA6AgEwoYPCN6g8A4v1wGvjXVgl/).

**A HASA apartment, July 2025.** "They'd be coming for me, if I hadn't
seroconverted and went to HASA right afterwards… I got the second apartment
shown me because I knew an order like this was coming." (2025-07-25,
https://facebook.com/723125492/posts/pfbid0yhQEZ86w2bHnavro8nyLCDRV9xpjJnbhFvHSgZ8cjJHjSXoAnvg8TXQJe2tYx15Ml/).
HASA is NYC's HIV/AIDS Services Administration; the post also discloses his
HIV seroconversion. This is the most precisely dated residence event in the
whole corpus: a new apartment secured in July 2025 through the city's
HIV-services housing apparatus.

## Mapping to life areas

| period | residence (evidence grade) | life area |
|---|---|---|
| ~1985–~2000 | Downey, CA (education record only) | childhood; pre-corpus |
| ~2000–~2002 | Los Angeles (one anniversary post; USC undated) | quasi-outness ("quasi-public… folks who know me deeply"), ONE Archives circle |
| ~2002–2010s | NYC, neighborhood unknown; "two or more homes" / "home in my backpack" | office jobs (2010 fingerprinting gig, 2014 "at the office"); Columbia undated |
| by 2021–2024 | Brooklyn (IG caption 2021; profile current_city) | arts-venue job (grantwriting/budgets, 2021), then gig work — Uber Eats delivery on foot and by subway, "three avenues and five streets… from Houston… to midtown" (2024-01-18) |
| Jan 2025 | move; "packing before being homeless" | precarity; Mayor Adams-era NYC as antagonist |
| Jul 2025 → | HASA apartment (second one shown) | HIV seroconversion disclosed same post; the city's care apparatus as landlord-of-last-resort |

## What the corpus will not give

No street addresses, no building names, no lease dates, no neighborhood for
the 2002–2020 stretch. The 2012/2017 silent years (`META_EXPORT.md`) fall
exactly where a residence history would most want coverage. The "two or more
homes" passage suggests the question "where did he live" may be the wrong
shape for much of this life — the corpus answers "with whom" and "how many
at once" more readily than "where." That is a finding about the archive, not
a failure of the search: `meta_residences.py` matched 55 unique candidates
and nearly all location hits were other people's places (a hookup's Hell's
Kitchen apartment, 2023-11-07), workplaces, or jokes.
