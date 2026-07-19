#!/usr/bin/env python3
"""Generate the unified XML collection (XML/) from the unified JSON collection (JSON/).

Every output file shares one dialect that mirrors the JSON structure, so apps
can switch between bible versions (and between the XML and JSON forms) without
special-casing:

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

Rules:
  * File names match the JSON collection: {code}_{Language}_{Version}[_{year}].xml
  * Verse text is the verse element's direct text; empty verses are <verse .../>.
  * The few translator study notes are child elements: <note>...</note> after
    the verse text (verse .text still holds the scripture text only).
  * UTF-8 throughout; all Unicode preserved.

Usage: python3 scripts/json_to_xml.py [--json JSON] [--out XML] [files...]
"""
import argparse
import glob
import json
import os
import sys
from xml.sax.saxutils import escape, quoteattr


def attrs(pairs):
    """Serialise (name, value) pairs, skipping None values."""
    return "".join(f" {k}={quoteattr(str(v))}" for k, v in pairs if v is not None)


def write_xml(d, fp):
    w = fp.write
    w('<?xml version="1.0" encoding="UTF-8"?>\n')
    w(f'<bible format={quoteattr(d.get("format", "bible.json/1").replace("json", "xml"))}>\n')
    w(" <metadata>\n")
    lang = d["language"]
    w(f'  <language{attrs([("code", lang["code"]), ("name", lang["name"])])}/>\n')
    ver = d["version"]
    w(f'  <version{attrs([("code", ver["code"]), ("year", ver["year"])])}/>\n')
    w(f'  <title>{escape(d.get("title", ""))}</title>\n')
    src = d["source"]
    w(f'  <source{attrs([("file", src["file"]), ("format", src["format"])])}>\n')
    for k, v in src.get("attributes", {}).items():
        w(f'   <attribute{attrs([("name", k), ("value", v)])}/>\n')
    w("  </source>\n")
    w(" </metadata>\n")
    w(" <books>\n")
    for b in d["books"]:
        w(f'  <book{attrs([("number", b["number"]), ("id", b["id"]), ("name", b["name"]), ("testament", b["testament"])])}>\n')
        for c in b["chapters"]:
            w(f'   <chapter{attrs([("number", c["chapter"])])}>\n')
            for v in c["verses"]:
                num = attrs([("number", v["verse"])])
                text = v.get("text", "")
                notes = "".join(f"<note>{escape(n)}</note>" for n in v.get("notes", []))
                if text or notes:
                    w(f"    <verse{num}>{escape(text)}{notes}</verse>\n")
                else:
                    w(f"    <verse{num}/>\n")
            w("   </chapter>\n")
        w("  </book>\n")
    w(" </books>\n")
    w("</bible>\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="JSON")
    ap.add_argument("--out", default="XML")
    ap.add_argument("files", nargs="*", help="convert only these JSON files")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    names = args.files or sorted(glob.glob(os.path.join(args.json, "*.json")))
    names = [n for n in names if os.path.basename(n) != "index.json"]
    done = failed = 0
    for i, path in enumerate(names, 1):
        try:
            d = json.load(open(path, encoding="utf-8"))
            target = os.path.splitext(os.path.basename(path))[0] + ".xml"
            tmp = os.path.join(args.out, target + ".tmp")
            with open(tmp, "w", encoding="utf-8") as fp:
                write_xml(d, fp)
            os.replace(tmp, os.path.join(args.out, target))
            done += 1
        except Exception as e:
            failed += 1
            print(f"FAILED {path}: {e}", flush=True)
        if i % 50 == 0:
            print(f"{i}/{len(names)} processed", flush=True)
    print(f"done={done} failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
