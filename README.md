# Bibles — unified XML and JSON collections

Bible translations in 300+ languages (1,000+ versions), each available in two
consistent machine-readable forms so apps can switch between versions and
formats without special-casing:

| folder | contents |
|---|---|
| [`XML/`](XML) | 1,087 bibles in one unified XML dialect — see [`XML/README.md`](XML/README.md) |
| [`JSON/`](JSON) | the same 1,087 bibles as JSON, plus `index.json` (catalogue) — see [`JSON/README.md`](JSON/README.md) |
| [`scripts/`](scripts) | the converters and the language/version naming map |

All files are named `{language code}_{Language name}_{Version}[_{year}]`
(ISO 639-1 codes where available, otherwise ISO 639-3), share the same
book/chapter/verse structure with canonical book numbers and stable 3-letter
book ids, and preserve all Unicode exactly. Duplicate copies of the same
translation were discarded during conversion (verified verse by verse); the
log is in [`JSON/README.md`](JSON/README.md).

The original source XMLs (mixed dialects, original filenames) are preserved on
git history, browsable at commit [`4ae2ac9`](../../tree/4ae2ac9).

---

Source collection: XML bibles gathered over 15 years, courtesy of
[beblia.com](https://beblia.com) (andrey@beblia.com) — "Use at your own
discretion, no need to ask for permission, no warranties."
