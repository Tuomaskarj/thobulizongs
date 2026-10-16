#!/usr/bin/env python3
"""
Kokoaa CMS-sisällön (_uutiset, _keikat, _settilista, _palautteet, _videot,
_sisalto) kahteen tiedostoon:

  data.json  — kaikki sisältö yhtenä tiedostona, jonka sivut lataavat
  feed.xml   — RSS-feedi uutisista

Ajetaan Netlifyn build-komennossa, joten tiedostot ovat aina ajan tasalla
eikä erillisiä GitHub Action -committeja tarvita.

Paikallinen ajo: python3 scripts/build.py
"""

import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

SITE_URL = "https://bulizongs.fi"
SITE_TITLE = "Thö Bulizongs – Uutiset"
SITE_DESC = "Ajankohtaista Thö Bulizongs -orkesterilta"

# Repon juuri = tämän skriptin yläkansio
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────────
#  Frontmatterin jäsennys
# ─────────────────────────────────────────────

def parse_frontmatter(text):
    """
    Palauttaa (kentät, leipäteksti).

    Decap tallentaa yleensä muodossa:
        ---
        title: Jotain
        ---
        Leipätekstiä

    mutta jättää joskus --- viivat pois. Molemmat tuetaan. Olennaista on,
    että leipätekstiä ei koskaan tulkita kentiksi — muuten rivi kuten
    "sama lupaus: tanssitakuu" päätyisi kentäksi.
    """
    text = text.replace("\r\n", "\n").lstrip("﻿")

    match = re.match(r"^---[ \t]*\n(.*?)\n---[ \t]*\n?", text, re.DOTALL)
    if match:
        block = match.group(1)
        body = text[match.end():]
    else:
        # Ei --- viivoja: kentät ovat alun peräkkäiset "avain: arvo" -rivit,
        # loput on leipätekstiä.
        lines = text.split("\n")
        cut = 0
        for i, line in enumerate(lines):
            if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*[ \t]*:", line) or (
                line.startswith((" ", "\t")) and i > 0
            ):
                cut = i + 1
            elif line.strip() == "":
                cut = i + 1
                break
            else:
                break
        block = "\n".join(lines[:cut])
        body = "\n".join(lines[cut:])

    fields = {}
    current = None
    for line in block.split("\n"):
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)[ \t]*:(.*)$", line)
        if m:
            current = m.group(1)
            fields[current] = clean_value(m.group(2))
        elif current and line.startswith((" ", "\t")):
            # Monirivinen arvo
            fields[current] = (fields[current] + " " + line.strip()).strip()

    fields["body"] = body.strip()
    return fields


def clean_value(raw):
    """Siistii yhden kentän arvon: välilyönnit, lainausmerkit, YAML-kommentit."""
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def read_md(path):
    with open(path, "r", encoding="utf-8") as fh:
        return parse_frontmatter(fh.read())


def collect(folder):
    """Lukee kansion kaikki .md-tiedostot slug mukana."""
    items = []
    for path in sorted(glob.glob(os.path.join(ROOT, folder, "*.md"))):
        item = read_md(path)
        item["slug"] = os.path.basename(path)[:-3]
        items.append(item)
    return items


# ─────────────────────────────────────────────
#  Apurit
# ─────────────────────────────────────────────

def date_key(item):
    """Lajitteluavain: ISO-päivämäärä tai tyhjä."""
    return (item.get("date") or "")[:10]


def strip_markdown(md):
    md = re.sub(r"\\\s*$", "", md, flags=re.MULTILINE)
    md = re.sub(r"^#{1,6}\s+", "", md, flags=re.MULTILINE)
    md = re.sub(r"\*\*(.*?)\*\*", r"\1", md)
    md = re.sub(r"\*(.*?)\*", r"\1", md)
    md = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", md)
    return " ".join(md.split()).strip()


def xml_escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def rfc822(date_str):
    try:
        return datetime.fromisoformat(date_str[:10]).strftime(
            "%a, %d %b %Y 12:00:00 +0000"
        )
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


# ─────────────────────────────────────────────
#  data.json
# ─────────────────────────────────────────────

def build_data():
    uutiset = sorted(collect("_uutiset"), key=date_key, reverse=True)
    keikat = sorted(collect("_keikat"), key=date_key)
    settilista = collect("_settilista")
    palautteet = collect("_palautteet")
    videot = sorted(
        collect("_videot"),
        key=lambda v: int(v["order"]) if v.get("order", "").isdigit() else 99,
    )

    sisalto_path = os.path.join(ROOT, "_sisalto", "etusivu.md")
    sisalto = read_md(sisalto_path) if os.path.exists(sisalto_path) else {}

    data = {
        "generoitu": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sisalto": sisalto,
        "uutiset": uutiset,
        "keikat": keikat,
        "settilista": settilista,
        "palautteet": palautteet,
        "videot": videot,
    }

    out = os.path.join(ROOT, "data.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(
        "data.json: "
        f"{len(uutiset)} uutista, {len(keikat)} keikkaa, "
        f"{len(settilista)} kappaletta, {len(palautteet)} palautetta, "
        f"{len(videot)} videota"
    )
    return data


# ─────────────────────────────────────────────
#  feed.xml
# ─────────────────────────────────────────────

def build_feed(uutiset):
    items = []
    for u in uutiset:
        title = xml_escape(u.get("title") or "Uutinen")
        excerpt = xml_escape(u.get("excerpt") or strip_markdown(u.get("body", ""))[:300])
        link = f"{SITE_URL}/uutiset.html#{u['slug']}"
        items.append(
            "    <item>\n"
            f"      <title>{title}</title>\n"
            f"      <link>{link}</link>\n"
            f"      <description>{excerpt}</description>\n"
            f"      <pubDate>{rfc822(u.get('date', ''))}</pubDate>\n"
            f"      <guid isPermaLink=\"true\">{link}</guid>\n"
            "    </item>"
        )

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{xml_escape(SITE_TITLE)}</title>\n"
        f"    <link>{SITE_URL}</link>\n"
        f"    <description>{xml_escape(SITE_DESC)}</description>\n"
        "    <language>fi</language>\n"
        f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />\n'
        f"    <lastBuildDate>{datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>\n"
        + "\n".join(items)
        + ("\n" if items else "")
        + "  </channel>\n"
        "</rss>\n"
    )

    with open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8") as fh:
        fh.write(feed)

    print(f"feed.xml: {len(items)} uutista")


# ─────────────────────────────────────────────

def main():
    data = build_data()
    build_feed(data["uutiset"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
