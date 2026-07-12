#!/usr/bin/env python3
"""Convert every bible XML on this repository's master branch to a unified JSON layout.

Both source formats are handled:
  * Zefania XML:  <XMLBIBLE><BIBLEBOOK bnumber bname><CHAPTER cnumber><VERS vnumber>
  * bible XML:    <bible><testament name><book number><chapter number><verse number>

Every output file shares one structure so consuming apps can switch between
translations freely:

    {
      "format": "bible.json/1",
      "language": {"code": "...", "name": "..."},
      "version": {"code": "...", "year": 2004 | null},
      "title": "<title metadata from the source file>",
      "source": {"file": "...", "format": "zefania" | "bible", "attributes": {...}},
      "books": [
        {"number": 1, "id": "GEN", "name": "Genesis", "testament": "OT",
         "chapters": [
           {"chapter": 1,
            "verses": [ {"verse": 1, "text": "..."} , ...]}
         ]}
      ]
    }

Verse text is Unicode, preserved exactly apart from whitespace normalisation
(json ensure_ascii=False, UTF-8 output). Empty verses are kept as "" so verse
numbering stays intact. Study notes (Zefania <NOTE>) are removed from the text
and kept in an optional per-verse "notes" list.

Usage:  python3 scripts/xml_to_json.py [--ref origin/master] [--out JSON] [files...]
"""
import argparse
import io
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from naming_map import DISCARD, resolve

# Standard Protestant 66-book numbering, plus the Zefania deuterocanonical
# numbers used by the Latin bibles in this collection (67+).
BOOKS = {
    1: ("GEN", "Genesis"), 2: ("EXO", "Exodus"), 3: ("LEV", "Leviticus"),
    4: ("NUM", "Numbers"), 5: ("DEU", "Deuteronomy"), 6: ("JOS", "Joshua"),
    7: ("JDG", "Judges"), 8: ("RUT", "Ruth"), 9: ("1SA", "1 Samuel"),
    10: ("2SA", "2 Samuel"), 11: ("1KI", "1 Kings"), 12: ("2KI", "2 Kings"),
    13: ("1CH", "1 Chronicles"), 14: ("2CH", "2 Chronicles"), 15: ("EZR", "Ezra"),
    16: ("NEH", "Nehemiah"), 17: ("EST", "Esther"), 18: ("JOB", "Job"),
    19: ("PSA", "Psalms"), 20: ("PRO", "Proverbs"), 21: ("ECC", "Ecclesiastes"),
    22: ("SNG", "Song of Solomon"), 23: ("ISA", "Isaiah"), 24: ("JER", "Jeremiah"),
    25: ("LAM", "Lamentations"), 26: ("EZK", "Ezekiel"), 27: ("DAN", "Daniel"),
    28: ("HOS", "Hosea"), 29: ("JOL", "Joel"), 30: ("AMO", "Amos"),
    31: ("OBA", "Obadiah"), 32: ("JON", "Jonah"), 33: ("MIC", "Micah"),
    34: ("NAM", "Nahum"), 35: ("HAB", "Habakkuk"), 36: ("ZEP", "Zephaniah"),
    37: ("HAG", "Haggai"), 38: ("ZEC", "Zechariah"), 39: ("MAL", "Malachi"),
    40: ("MAT", "Matthew"), 41: ("MRK", "Mark"), 42: ("LUK", "Luke"),
    43: ("JHN", "John"), 44: ("ACT", "Acts"), 45: ("ROM", "Romans"),
    46: ("1CO", "1 Corinthians"), 47: ("2CO", "2 Corinthians"),
    48: ("GAL", "Galatians"), 49: ("EPH", "Ephesians"), 50: ("PHP", "Philippians"),
    51: ("COL", "Colossians"), 52: ("1TH", "1 Thessalonians"),
    53: ("2TH", "2 Thessalonians"), 54: ("1TI", "1 Timothy"), 55: ("2TI", "2 Timothy"),
    56: ("TIT", "Titus"), 57: ("PHM", "Philemon"), 58: ("HEB", "Hebrews"),
    59: ("JAS", "James"), 60: ("1PE", "1 Peter"), 61: ("2PE", "2 Peter"),
    62: ("1JN", "1 John"), 63: ("2JN", "2 John"), 64: ("3JN", "3 John"),
    65: ("JUD", "Jude"), 66: ("REV", "Revelation"),
    67: ("JDT", "Judith"), 68: ("WIS", "Wisdom"), 69: ("TOB", "Tobit"),
    70: ("SIR", "Sirach"), 71: ("BAR", "Baruch"),
    72: ("1MA", "1 Maccabees"), 73: ("2MA", "2 Maccabees"),
}

BOOK_TAGS = {"book", "biblebook"}
VERSE_TAGS = {"verse", "vers"}


def norm_text(s):
    return " ".join(s.split())


def parse_num(raw):
    """Verse/chapter/book numbers are integers in this corpus; keep the raw
    string if a file ever deviates so no information is lost."""
    try:
        return int(raw)
    except (TypeError, ValueError):
        return raw


def testament_of(book_num, explicit):
    if explicit:
        e = explicit.strip().lower()
        if e.startswith("old"):
            return "OT"
        if e.startswith("new"):
            return "NT"
    if isinstance(book_num, int):
        if book_num <= 39:
            return "OT"
        if book_num <= 66:
            return "NT"
        return "DC"  # deuterocanon
    return None


def verse_payload(el):
    """Text of a verse element, with Zefania <NOTE> children split out."""
    notes = [norm_text("".join(n.itertext())) for n in el.iter() if n.tag.lower() == "note"]
    if notes:
        # rebuild text without note content
        parts = []

        def walk(node):
            if node.tag.lower() == "note":
                return
            if node.text:
                parts.append(node.text)
            for child in node:
                walk(child)
                if child.tail:
                    parts.append(child.tail)

        walk(el)
        return norm_text("".join(parts)), [n for n in notes if n]
    return norm_text("".join(el.itertext())), None


def convert(data, source_name):
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    root_tag = None
    root_attrs = {}
    cur_testament = None
    books = []
    book = None
    chapter = None
    for ev, el in ET.iterparse(io.BytesIO(data), events=("start", "end")):
        tag = el.tag.split("}")[-1].lower()
        if ev == "start":
            if root_tag is None:
                root_tag = tag
                root_attrs = {k.split("}")[-1]: v for k, v in el.attrib.items()}
            elif tag in ("testament", "testment"):
                cur_testament = el.get("name")
            elif tag in BOOK_TAGS:
                num = parse_num(el.get("bnumber") or el.get("number"))
                std = BOOKS.get(num) if isinstance(num, int) else None
                book = {
                    "number": num,
                    "id": std[0] if std else None,
                    "name": el.get("bname") or el.get("name") or (std[1] if std else None),
                    "testament": testament_of(num, cur_testament),
                    "chapters": [],
                }
                books.append(book)
            elif tag == "chapter":
                chapter = {"chapter": parse_num(el.get("cnumber") or el.get("number")),
                           "verses": []}
                book["chapters"].append(chapter)
        else:
            if tag in VERSE_TAGS:
                text, notes = verse_payload(el)
                verse = {"verse": parse_num(el.get("vnumber") or el.get("number")),
                         "text": text}
                if notes:
                    verse["notes"] = notes
                chapter["verses"].append(verse)
                el.clear()
            elif tag in BOOK_TAGS:
                el.clear()

    # drop stray empty book elements (e.g. the empty duplicate book 40 in PularBible.xml)
    books = [b for b in books if any(c["verses"] for c in b["chapters"])]

    fmt = "zefania" if root_tag == "xmlbible" else "bible"
    title = (root_attrs.get("translation") or root_attrs.get("language")
             or root_attrs.get("name") or root_attrs.get("biblename")
             or root_attrs.get("title") or "")
    code, lang, version, year, target = resolve(source_name, title)
    meta = {
        "format": "bible.json/1",
        "language": {"code": code, "name": lang},
        "version": {"code": version, "year": year},
        "title": norm_text(title),
        "source": {"file": source_name, "format": fmt, "attributes": root_attrs},
    }
    return target, meta, books


def dump(meta, books, fp):
    """Write JSON with one verse per line: compact but still diff/human friendly."""
    j = lambda o: json.dumps(o, ensure_ascii=False)
    fp.write("{\n")
    for k, v in meta.items():
        fp.write(f"{j(k)}: {j(v)},\n")
    fp.write('"books": [\n')
    for bi, b in enumerate(books):
        head = {k: b[k] for k in ("number", "id", "name", "testament")}
        fp.write("{" + f'{j("number")}: {j(head["number"])}, {j("id")}: {j(head["id"])}, '
                 f'{j("name")}: {j(head["name"])}, {j("testament")}: {j(head["testament"])}, '
                 '"chapters": [\n')
        for ci, c in enumerate(b["chapters"]):
            fp.write("{" + f'{j("chapter")}: {j(c["chapter"])}, "verses": [\n')
            for vi, v in enumerate(c["verses"]):
                fp.write(j(v) + (",\n" if vi < len(c["verses"]) - 1 else "\n"))
            fp.write("]}" + (",\n" if ci < len(b["chapters"]) - 1 else "\n"))
        fp.write("]}" + (",\n" if bi < len(books) - 1 else "\n"))
    fp.write("]}\n")


def git_blob(ref, path):
    return subprocess.check_output(["git", "cat-file", "blob", f"{ref}:{path}"])


def list_xml(ref):
    out = subprocess.check_output(["git", "ls-tree", "-r", "-z", "--name-only", ref])
    return [n for n in out.decode().split("\0") if n.lower().endswith(".xml")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/master")
    ap.add_argument("--out", default="JSON")
    ap.add_argument("files", nargs="*", help="convert only these source files")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    names = args.files or list_xml(args.ref)
    done = skipped = failed = 0
    for i, name in enumerate(names, 1):
        if name in DISCARD:
            skipped += 1
            continue
        try:
            target, meta, books = convert(git_blob(args.ref, name), name)
            tmp = os.path.join(args.out, target + ".tmp")
            with open(tmp, "w", encoding="utf-8") as fp:
                dump(meta, books, fp)
            os.replace(tmp, os.path.join(args.out, target))
            done += 1
        except Exception as e:  # keep going; report at the end
            failed += 1
            print(f"FAILED {name}: {e}", flush=True)
        if i % 50 == 0:
            print(f"{i}/{len(names)} processed", flush=True)
    print(f"done={done} skipped_duplicates={skipped} failed={failed}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
