# Bible JSON collection

Every file in this folder was generated from the XML bibles at the repository
root by [`scripts/xml_to_json.py`](../scripts/xml_to_json.py). All files share
one structure so an app can switch between any two translations without
special-casing.

## File naming

```
{language code}_{Language name}_{Version}[_{year}].json
```

* **language code** — ISO 639-1 (two letters) where the language has one,
  otherwise its ISO 639-3 code (three letters). Most of the world's languages
  have no two-letter code, so e.g. Acehnese is `ace`.
* **Language name** — English name of the language, CamelCase, no spaces.
* **Version** — the translation/version designation from the source file
  (`KJV`, `BSI`, `Synodal`, …). `Bible` when the source names no version.
* **year** — publication year when one is stated in the source filename or its
  title metadata; omitted when unknown.

Examples: `en_English_KJV_1769.json`, `am_Amharic_Bible.json`,
`ctd_TedimChin_TB77.json`, `grc_AncientGreek_SBLGNT.json`.

## Document structure

```jsonc
{
  "format": "bible.json/1",
  "language": {"code": "en", "name": "English"},
  "version":  {"code": "KJV", "year": 1769},        // year may be null
  "title":    "King James Version",                  // title metadata as found in the XML
  "source": {
    "file": "King James Version (1769).xml",         // XML file this was generated from
    "format": "zefania",                             // "zefania" or "bible" source dialect
    "attributes": { ... }                            // all root attributes, verbatim
  },
  "books": [
    {
      "number": 1,            // canonical book number (1-66; 67+ deuterocanon)
      "id": "GEN",            // stable 3-letter book id (USFM style), same across all files
      "name": "Genesis",      // book name from the source when present, else standard English
      "testament": "OT",      // "OT", "NT" or "DC" (deuterocanon)
      "chapters": [
        {"chapter": 1, "verses": [
          {"verse": 1, "text": "In the beginning ..."}
        ]}
      ]
    }
  ]
}
```

Notes:

* One verse per line in the raw file — friendly to diffs and streaming parsers.
* Text is UTF-8 with all Unicode preserved (no `\uXXXX` escaping); whitespace
  is normalised to single spaces.
* Empty verses are kept as `"text": ""` so verse numbering stays aligned with
  printed editions.
* A few sources carry translator study notes; these are kept out of the verse
  text in an optional `"notes": [...]` array on the verse.
* Book coverage varies with the source (many are New Testament only; `books`
  then contains only books 40-66). `number`/`id` are always canonical.
* `JSON/index.json` lists every file with its language, version, year, book
  and verse counts — a machine-readable catalogue of the collection.

## Duplicates discarded

Twenty-two source XMLs were not converted because they duplicate another
file's translation text (verified verse by verse). The kept counterpart and
reasons are recorded in `DISCARD` in
[`scripts/naming_map.py`](../scripts/naming_map.py):

| discarded source | kept instead |
|---|---|
| `EnglishAmplifiedBible.xml` | `Amplified Bible (1965).xml` |
| `Bengali Bible.xml` | `BengaliBSIBible.xml` |
| `ChinTedimBible.xml` | `ChinTB77Bible.xml` |
| `SongeBible.xml` | `KimiiruBible.xml` (mislabeled copy) |
| `Lithuanian2012KANBible.xml` | `Lithuanian2012EKUBible.xml` |
| `ChibembaBible.xml` | `BembaBible.xml` |
| `Holy Bible Revised Version (1885).xml` | `Revised Version (1881-1885).xml` |
| `EnglishHCSBBible.xml` | `Holman Christian Standard Bible (2004).xml` |
| `EnglishNRSVBible.xml` | `New Revised Standard Version (1989).xml` |
| `EnglishNASBBible.xml` | `New American Standard Bible (1995).xml` |
| `EnglishNETBible.xml` | `New English Translation (2005).xml` |
| `EnglishYLTBible.xml` | `Young's Literal Translation (1898).xml` |
| `Tamil Bible.xml` | `TamilBible.xml` |
| `The Darby Bible (1890).xml` | `EnglishDarbyBible.xml` (more complete copy) |
| `Cebuano1999Bible.xml` | `CebuanoRCPVBible.xml` (more complete copy) |
| `ChinTedim2011Bible.xml` | `ChinTDBBible.xml` |
| `EnglishNASUBible.xml` | `New American Bible.xml` (NASU label was wrong; text is the NAB) |
| `EnglishNIRVBible.xml` | `New International Reader's Version (1998).xml` |
| `EnglishTyndaleBible.xml` | `Tyndale-Rogers-Coverdale-Cranmer Bible (1537).xml` |
| `Romani2004Bible.xml` | `RomaniKALD2004Bible.xml` |
| `Romani2007Bible.xml` | `RomaniROM07Bible.xml` |
| `TagalogRevised2005Bible.xml` | `Tagalog2005Bible.xml` (more complete copy) |
