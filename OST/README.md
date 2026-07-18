# Open Scriptures Translation (OST)

An open, freely-licensed translation of the Christian Bible, with the goal of
one version in every language of the [`../JSON`](../JSON) collection — 282
languages and counting.

**License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**
(Creative Commons Attribution-ShareAlike 4.0 International).
The license is embedded in every file's metadata. It is irrevocable — once
published, the grant can never be withdrawn — and its ShareAlike clause means
every revision or derivative must remain under the same license: the text can
be sold, printed, and built upon, but never closed. Contributions are accepted
under the same license with no copyright assignment, which distributes the
copyright across all contributors and makes relicensing practically
impossible for anyone.

## Files

Same naming and structure as the rest of the repository:
`{language code}_{Language name}_OST.json`, one verse per line, with two extra
metadata blocks:

* `"license"` — the CC BY-SA 4.0 grant, machine-readable.
* `"status"` — where the text stands:
  * `"seed"` — an unrevised public-domain base text (see below);
  * `"draft"` — revision/translation in progress;
  * `"reviewed"` — checked by mother-tongue reviewers.

`index.json` catalogs every file with its stage and provenance.

## Tier 1 — public-domain seeds (current stage)

This folder currently holds **41 languages seeded from public-domain-era
translations** found in this repository — the same method the World English
Bible used (a revision of the public-domain ASV 1901). Each file's
`status.seeded_from` names its exact base; highlights: English ASV 1901,
German Luther 1912, French Segond 1910, Spanish Reina-Valera 1909, Chinese
Union Version 1919, Russian Synodal 1876, Arabic Smith-Van Dyck 1865, Dutch
Statenvertaling, Czech Kralická 1613. Eight languages are New Testament only
(cy, gd, gn, he, sq, sw + partials); the rest are full bibles.

Caveats recorded honestly:

* Public-domain status was assessed from publication years (≤1928) and
  explicit markings; **verify locally before redistribution**, since copyright
  terms vary by jurisdiction (life + 70 in much of the world).
* Romanian was deliberately *not* seeded: the Cornilescu lineage's
  public-domain status is contested.
* Classical languages (Ancient Greek, Latin, Literary Chinese) are source
  texts, not translation targets.

## Tier 2 — the remaining ~240 languages

Languages whose only available translations are copyrighted cannot be seeded
from them (a reworded copyrighted translation is still a derivative work).
They need fresh translation from the source texts — the collection includes
public-domain Hebrew (Leningrad, Aleppo) and Greek (Stephanus 1550, Byzantine)
bases — via human translators or AI-assisted drafts **with mother-tongue
review** before any file is marked `reviewed`.

## Roadmap

1. ✅ Seed from public-domain texts (41 languages)
2. Modernize seed languages book by book (`seed` → `draft` → `reviewed`)
3. Recruit mother-tongue reviewers per language
4. Draft Tier-2 languages from the source texts, review, and add
