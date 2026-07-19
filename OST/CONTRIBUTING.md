# Contributing to the Open Scriptures Translation

## The one rule that protects the project

**Never derive OST text from a copyrighted translation.** Rewording a
copyrighted bible is a derivative work no license can free. OST text may come
only from:

1. **Public-domain translations** (Tier 1 seeds — see `status.seeded_from` in
   each file);
2. **The original-language source texts** — this repository carries
   public-domain Hebrew (Leningrad, Aleppo) and Greek (Stephanus 1550,
   Byzantine, TR 1894) texts;
3. **Your own fresh translation work** from those sources.

Consulting a copyrighted translation to *understand* a passage is normal
scholarship; copying or lightly rephrasing its wording is not acceptable.

## Stages

Every file's `status.stage` declares its trust level, and per-book progress is
recorded in `status.progress`:

| stage | meaning |
|---|---|
| `seed` | unrevised public-domain base text |
| `draft` | new or modernized text, from sources above, **not yet reviewed** |
| `reviewed` | checked by at least two mother-tongue reviewers |

## AI-assisted drafting

AI drafts are welcome under exactly these conditions:

* translated from the source texts (rule above), never from copyrighted
  translations;
* committed only as `stage: "draft"`, with `status.method` stating the tool
  and source text used;
* **mother-tongue review is mandatory** before a book can be marked
  `reviewed` — no exceptions. A draft is a starting point for reviewers, not
  scripture.

The Tier-2 pilot (`ko_Korean_OST.json`, Mark 1) is the reference example.

## Review

Marking a book `reviewed` requires two independent mother-tongue reviewers
confirming accuracy against the source text and natural contemporary
wording. Record reviewer names/handles in `status.reviewers`.

## License terms of contribution

By contributing you agree your work is published under
**CC BY-SA 4.0** with **no copyright assignment** — you keep your copyright
and grant the irrevocable license. Copyright spread across many contributors
is deliberate: it makes relicensing (open or closed) practically impossible
for anyone, forever.
