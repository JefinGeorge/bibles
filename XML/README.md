# Bible XML collection (unified format)

Every file in this folder is generated from the matching file in
[`../JSON`](../JSON) by [`scripts/json_to_xml.py`](../scripts/json_to_xml.py).
All files share one XML dialect so an app can switch between any two bible
versions — or between the XML and JSON form of the same version — without
special-casing. The original source XMLs (mixed dialects) remain available on
the `master` branch.

## File naming

Identical to the JSON collection:

```
{language code}_{Language name}_{Version}[_{year}].xml
```

ISO 639-1 (two-letter) codes where the language has one, otherwise ISO 639-3.
Examples: `en_English_KJV_1769.xml`, `am_Amharic_Bible.xml`,
`ctd_TedimChin_TB77.xml`, `grc_AncientGreek_SBLGNT.xml`.

## Document structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bible format="bible.xml/1">
 <metadata>
  <language code="en" name="English"/>
  <version code="KJV" year="1769"/>          <!-- year omitted when unknown -->
  <title>King James Version</title>
  <source file="King James Version (1769).xml" format="zefania">
   <attribute name="biblename" value="King James Version"/>
  </source>
 </metadata>
 <books>
  <book number="1" id="GEN" name="Genesis" testament="OT">
   <chapter number="1">
    <verse number="1">In the beginning God created the heaven and the earth.</verse>
   </chapter>
  </book>
 </books>
</bible>
```

Notes:

* `book number` is the canonical book number (1–66, 67+ for deuterocanon);
  `id` is the stable 3-letter book id (USFM style), identical across every
  file; `testament` is `OT`, `NT` or `DC`.
* Verse text is the `<verse>` element's direct text. Empty verses are kept as
  `<verse number="N"/>` so verse numbering stays aligned with printed editions.
* A few sources carry translator study notes; they follow the verse text as
  `<note>` child elements (the verse's `.text` is always scripture only).
* `<source>` records which original XML the data came from, its dialect, and
  its root attributes verbatim.
* UTF-8 throughout; all Unicode is preserved exactly.
* Duplicate versions were discarded during conversion — see the table in
  [`../JSON/README.md`](../JSON/README.md).
