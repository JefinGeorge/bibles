#!/usr/bin/env python3
"""Seed the Open Scriptures Translation (OST) from public-domain base texts.

Tier 1 of the OST project: for every language where this repository holds a
public-domain-era translation, copy that text into the OST folder as the
starting base for revision. Each output file keeps the collection's unified
JSON structure and adds `license` and `status` blocks so the license travels
with the data and the revision state of the text is always explicit.

The version name/code are parameters below so the project can be renamed
with a one-line change.

Usage: python3 scripts/seed_ost.py [--json JSON] [--out OST]
"""
import argparse
import json
import os
import sys

VERSION_CODE = "OST"
VERSION_NAME = "Open Scriptures Translation"
LICENSE = {
    "name": "CC BY-SA 4.0",
    "url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "note": ("Creative Commons Attribution-ShareAlike 4.0 International. "
             "Irrevocable; all derivative works must carry this same license."),
}
SEED_NOTE = ("Unrevised public-domain base text serving as the starting point for the "
             + VERSION_NAME + ". Verify public-domain status in your jurisdiction "
             "before redistribution; the text is awaiting modernization and review.")

# language code -> source file in JSON/ chosen as the public-domain seed.
# Selection favours texts that are unambiguously public domain (pre-1929 or
# explicitly marked) and, where several qualify, the edition history has
# proven usable as a revision base (e.g. ASV 1901 -> World English Bible).
SEEDS = {
    "ar": "ar_Arabic_SVD_1865.json",            # Smith-Van Dyck, marked public domain
    "bg": "bg_Bulgarian_Verens_1871.json",      # Tsarigrad translation 1871
    "cs": "cs_Czech_Kralichka_1613.json",       # Bible kralická 1613
    "cy": "cy_Welsh_Bible_1894.json",           # NT only
    "da": "da_Danish_Bible.json",               # Danske Bibel 1871/1907
    "de": "de_German_Luther_1912.json",         # Luther 1912
    "ee": "ee_Ewe_Bible_1913.json",
    "el": "el_Greek_Modern_1904.json",
    "en": "en_English_ASV_1901.json",           # ASV 1901 (base of the WEB)
    "eo": "eo_Esperanto_Bible_1926.json",       # Londona Biblio
    "es": "es_Spanish_Bible_1909.json",         # Reina-Valera 1909
    "fa": "fa_Persian_Bible_1895.json",         # Old Persian Version
    "fi": "fi_Finnish_Bible_1776.json",         # Biblia 1776
    "fr": "fr_French_Bible_1910.json",          # Louis Segond 1910
    "ga": "ga_Irish_Bible_1817.json",           # Bedell/O'Donnell lineage
    "gd": "gd_ScottishGaelic_Bible_1875.json",  # NT only
    "gn": "gn_Guarani_Bible_1913.json",         # NT only
    "he": "he_Hebrew_Bible_1885.json",          # Delitzsch Hebrew NT
    "hu": "hu_Hungarian_Karoli_1908.json",      # Károli revision 1908
    "hy": "hy_Armenian_Ararat_1896.json",       # Ararat translation
    "id": "id_Indonesian_TL_1954.json",         # Terjemahan Lama (Klinkert/Bode lineage)
    "it": "it_Italian_Riveduta.json",           # Riveduta 1924 (Luzzi d. 1948)
    "lv": "lv_Latvian_Gluck_1685.json",         # Glück 1685
    "mg": "mg_Malagasy_Bible_1865.json",
    "ml": "ml_Malayalam_Bible_1910.json",
    "my": "my_Burmese_Bible_1928.json",         # Judson lineage
    "ngl": "ngl_Lomwe_Bible_1930.json",         # NT only, published 1930
    "nl": "nl_Dutch_Bible.json",                # Statenvertaling (Jongbloed edition)
    "no": "no_Norwegian_Bible_1921.json",
    "or": "or_Odia_Bible_1840.json",
    "pl": "pl_Polish_Gdansk.json",              # Biblia Gdańska 1881-1910 revision
    "pt": "pt_Portuguese_Almeida_1753.json",    # Almeida 1753, marked public domain
    "ru": "ru_Russian_Synodal_1876.json",       # Synodal translation
    "sl": "sl_Slovenian_Chraska_1914.json",     # Chráska
    "sq": "sq_Albanian_Bible_1879.json",        # NT only
    "sr": "sr_Serbian_Latin_1865.json",         # Karadžić-Daničić, Latin script
    "sv": "sv_Swedish_Bible_1917.json",         # 1917 års översättning
    "sw": "sw_Swahili_SWZZB_1921.json",         # NT only
    "te": "te_Telugu_Bible_1880.json",
    "tl": "tl_Tagalog_Bible.json",              # Ang Biblia 1905 -- CONFIRM the text is the
                                                # 1905 edition, not the 1982 revision
    "tn": "tn_Tswana_Bible_1890.json",
    "ts": "ts_Tsonga_Bible_1929.json",          # published 1929
    "uk": "uk_Ukrainian_Bible_1905.json",       # Kulish translation
    "vi": "vi_Vietnamese_Bible_1925.json",      # 1925 translation
    "xh": "xh_Xhosa_Bible_1920.json",
    "zh": "zh_Chinese_Traditional_1919.json",   # Chinese Union Version 1919
}

# Deliberately not seeded despite public-domain-era texts in the collection:
#   grc, la, lzh - classical/source languages, not living translation targets
#   ro          - the Cornilescu lineage's public-domain status is contested
#   ny          - the corpus Chichewa file is the 2014 Buku Lopatulika revision
#                 (copyrighted), not the public-domain 1922 text its title cites


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="JSON")
    ap.add_argument("--out", default="OST")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    index = []
    for code, src_name in sorted(SEEDS.items()):
        src_path = os.path.join(args.json, src_name)
        d = json.load(open(src_path, encoding="utf-8"))
        lang = d["language"]
        assert lang["code"] == code, f"{src_name}: expected {code}, got {lang['code']}"
        out = {
            "format": d["format"],
            "language": lang,
            "version": {"code": VERSION_CODE, "name": VERSION_NAME, "year": None},
            "title": f"{VERSION_NAME} — {lang['name']}",
            "license": LICENSE,
            "status": {
                "stage": "seed",
                "seeded_from": src_name,
                "seed_title": d["title"],
                "seed_year": d["version"]["year"],
                "note": SEED_NOTE,
            },
            "source": d["source"],
            "books": d["books"],
        }
        target = f"{code}_{lang['name']}_{VERSION_CODE}.json"
        # reuse the collection's one-verse-per-line writer
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from xml_to_json import dump
        meta = {k: v for k, v in out.items() if k != "books"}
        tmp = os.path.join(args.out, target + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fp:
            dump(meta, out["books"], fp)
        os.replace(tmp, os.path.join(args.out, target))
        nverses = sum(len(c["verses"]) for b in out["books"] for c in b["chapters"])
        index.append({
            "file": target, "language": lang,
            "stage": "seed", "seeded_from": src_name,
            "books": len(out["books"]), "verses": nverses,
        })
        print(f"seeded {target} <- {src_name} ({len(out['books'])} books)")

    with open(os.path.join(args.out, "index.json"), "w", encoding="utf-8") as fp:
        json.dump({"format": "bible.json-index/1", "version": VERSION_NAME,
                   "license": LICENSE, "count": len(index), "bibles": index},
                  fp, ensure_ascii=False, indent=1)
    print(f"done: {len(index)} languages seeded; wrote {args.out}/index.json")


if __name__ == "__main__":
    main()
