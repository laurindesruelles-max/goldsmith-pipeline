"""Echte Quellen für Goldsmith – NUR Material, das für monetarisierte Videos zulässig ist.
(Sorgfaltspraxis, keine Rechtsberatung.)

ZULÄSSIG
- Fotos: Wikimedia Commons nur mit Public Domain, CC0, CC BY, CC BY-SA (NC = nicht kommerziell und ND = keine
  Bearbeitung werden automatisch abgelehnt; ebenso „fair use“/unklare Lizenz). Library of Congress nur mit
  „No known restrictions“. NASA (gemeinfrei; keine NASA-Logos, keine Werbe-Andeutung).
- Personen: nur Personen des öffentlichen Lebens (eigener Wikipedia-Artikel) im sachlichen Zusammenhang der Story,
  Foto unverändert (Ausschnitt/Zoom ok, keine KI-Bearbeitung, kein Montage-Kontext, der etwas Falsches unterstellt).
  NIE Opfer, Kinder oder Privatpersonen.
- Dokumente: US-Gerichtsentscheidungen (Urteile sind gemeinfrei), Behörden-Pressemitteilungen (SEC, DOJ, FTC),
  deutsche Gesetze/Urteile (§ 5 UrhG). Firmen-Unterlagen bei der SEC (10-K, 20-F …) stammen von der Firma →
  nur KURZE wörtliche Auszüge als Beleg (Zitat), nie ganze Seiten.
- Presseartikel: nur kurzes Zitat (Überschrift/1 Satz) in unserem eigenen Layout + „Quelle: Medium, Datum“.
  KEINE Screenshots, Logos, Fotos oder Layouts von Zeitungen/Websites.
- Zahlen: Daten sind frei → eigene Diagramme mit Quellenangabe.

Jedes verwendete Material landet mit Lizenz in credits.json → Bildnachweise in der Beschreibung + Prüfbericht qa.md.
Benötigte Domain-Freigaben: commons.wikimedia.org, upload.wikimedia.org, www.loc.gov, tile.loc.gov,
images-api.nasa.gov, images-assets.nasa.gov, www.sec.gov, efts.sec.gov, www.courtlistener.com

usage (Kommandozeile):
  python3 engine/sources.py commons "Leonardo Del Vecchio" 5 <img_dir> [--person]
  python3 engine/sources.py loc "assembly line 1950s" 5 <img_dir>
  python3 engine/sources.py nasa "apollo 11" 3 <img_dir>
  python3 engine/sources.py sec "Luxottica" "destroyed" <out.txt>      (Volltextsuche in SEC-Unterlagen)
  python3 engine/sources.py court "Oakley Luxottica" 3                 (Gerichtsentscheidungen)
  python3 engine/sources.py credits <img_dir>                          (Bildnachweise für die Beschreibung)
"""
import os, re, sys, json, html, urllib.parse, urllib.request, urllib.error

UA = "GoldsmithResearchBot/1.0 (https://github.com/laurindesruelles-max/goldsmith-pipeline; YouTube documentary research) python-urllib"
OK_LIC = re.compile(r"^(pd|public domain|cc0|cc[- ]?zero|cc[- ]by(-sa)?[- ]?\d|cc[- ]by(-sa)?$|no restrictions)", re.I)
BAD_LIC = re.compile(r"\b(nc|nd|non-?commercial|no ?deriv|fair use|all rights reserved|copyrighted|trademark)\b", re.I)


def _get(url, binary=False, timeout=60, tries=4):
    import time
    for k in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, */*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and k < tries-1: time.sleep(5*(k+1)); continue
            raise


def _clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def license_ok(short):
    s = (short or "").strip()
    if not s or BAD_LIC.search(s): return False
    return bool(OK_LIC.search(s)) or s.lower() in ("public domain", "pd-us", "pd-usgov", "pd-old")


def _save_credit(img_dir, entry):
    p = f"{img_dir}/credits.json"; cr = json.load(open(p)) if os.path.exists(p) else []
    cr = [c for c in cr if c["file"] != entry["file"]] + [entry]
    json.dump(cr, open(p, "w"), indent=1, ensure_ascii=False)


# ------------------------------------------------------------------ Wikimedia Commons
def commons(query, n, img_dir, person=False, width=1920):
    """Sucht Fotos mit zulässiger Lizenz, lädt sie nach img_dir/real_<slug>_k.jpg, protokolliert die Lizenz."""
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 40,
        "gsrsearch": f"{query} filetype:bitmap", "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": width})
    pages = json.loads(_get(api)).get("query", {}).get("pages", {})
    os.makedirs(img_dir, exist_ok=True); got = []
    for p in sorted(pages.values(), key=lambda x: x.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]; m = ii.get("extmetadata", {})
        lic = _clean(m.get("LicenseShortName", {}).get("value", ""))
        if not license_ok(lic) or ii.get("mime") not in ("image/jpeg", "image/png"): continue
        if ii.get("width", 0) < 900: continue
        restr = _clean(m.get("Restrictions", {}).get("value", ""))
        if "trademark" in restr.lower(): continue
        if person and "personality" in restr.lower(): pass   # Persönlichkeitsrechte: Hinweis in credits (sachlicher Kontext Pflicht)
        url = ii.get("thumburl") or ii["url"]; fn = f"real_{re.sub(r'[^a-z0-9]+', '_', query.lower())[:30]}_{len(got)+1}.jpg"
        open(f"{img_dir}/{fn}", "wb").write(_get(url, binary=True))
        entry = {"file": fn, "source": "Wikimedia Commons", "page": ii.get("descriptionurl"), "title": p.get("title"),
                 "author": _clean(m.get("Artist", {}).get("value", "")) or "unbekannt", "license": lic,
                 "license_url": m.get("LicenseUrl", {}).get("value", ""), "person": person, "restrictions": restr,
                 "credit": f"{_clean(m.get('Artist', {}).get('value', '')) or 'Wikimedia Commons'} / {lic}"}
        _save_credit(img_dir, entry); got.append(entry)
        if len(got) >= n: break
    return got


# ------------------------------------------------------------------ Library of Congress
def loc(query, n, img_dir):
    api = "https://www.loc.gov/photos/?" + urllib.parse.urlencode({"q": query, "fo": "json", "c": 50})
    res = json.loads(_get(api)).get("results", []); os.makedirs(img_dir, exist_ok=True); got = []
    for r in res:
        rights = " ".join(r.get("rights_advisory", []) if isinstance(r.get("rights_advisory"), list) else [str(r.get("rights_advisory", ""))])
        if "no known restrictions" not in rights.lower(): continue
        imgs = [u for u in r.get("image_url", []) if u.endswith(".jpg")]
        if not imgs: continue
        url = imgs[-1].split("#")[0]; fn = f"real_loc_{re.sub(r'[^a-z0-9]+', '_', query.lower())[:24]}_{len(got)+1}.jpg"
        open(f"{img_dir}/{fn}", "wb").write(_get(url, binary=True))
        entry = {"file": fn, "source": "Library of Congress", "page": r.get("url"), "title": r.get("title"),
                 "author": ", ".join(r.get("contributor", [])[:2]) if isinstance(r.get("contributor"), list) else "",
                 "license": "No known restrictions on publication", "license_url": "https://www.loc.gov/legal/", "person": False,
                 "credit": "Library of Congress"}
        _save_credit(img_dir, entry); got.append(entry)
        if len(got) >= n: break
    return got


# ------------------------------------------------------------------ NASA
def nasa(query, n, img_dir):
    api = "https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": query, "media_type": "image"})
    items = json.loads(_get(api)).get("collection", {}).get("items", []); os.makedirs(img_dir, exist_ok=True); got = []
    for it in items:
        d = (it.get("data") or [{}])[0]; nid = d.get("nasa_id")
        if not nid or "logo" in (d.get("title", "") + " ".join(d.get("keywords", []) or [])).lower(): continue
        assets = json.loads(_get(f"https://images-api.nasa.gov/asset/{urllib.parse.quote(nid)}")).get("collection", {}).get("items", [])
        urls = [a["href"] for a in assets if a["href"].endswith(("~large.jpg", "~orig.jpg"))]
        if not urls: continue
        fn = f"real_nasa_{len(got)+1}.jpg"; open(f"{img_dir}/{fn}", "wb").write(_get(urls[0].replace("http://", "https://"), binary=True))
        entry = {"file": fn, "source": "NASA", "page": f"https://images.nasa.gov/details/{nid}", "title": d.get("title"),
                 "author": d.get("photographer") or d.get("center") or "NASA", "license": "Public Domain (NASA)",
                 "license_url": "https://www.nasa.gov/nasa-brand-center/images-and-media/", "person": False, "credit": "NASA"}
        _save_credit(img_dir, entry); got.append(entry)
        if len(got) >= n: break
    return got


# ------------------------------------------------------------------ SEC (Firmen-Unterlagen: nur kurze Zitate!)
def sec(company, phrase, out=None, forms="10-K,20-F,8-K,DEF 14A"):
    """Volltextsuche: findet Unterlagen, in denen `phrase` vorkommt, und gibt die Fundstelle (±300 Zeichen) zurück."""
    api = "https://efts.sec.gov/LATEST/search-index?" + urllib.parse.urlencode({"q": f'"{phrase}" "{company}"', "forms": forms})
    hits = json.loads(_get(api)).get("hits", {}).get("hits", [])[:5]; res = []
    for h in hits:
        s = h.get("_source", {}); adsh = h["_id"].split(":")[0]; fn = h["_id"].split(":")[1]
        cik = (s.get("ciks") or [""])[0].lstrip("0")
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
        try: txt = _clean(_get(url))
        except Exception: continue
        i = txt.lower().find(phrase.lower())
        if i < 0: continue
        res.append({"form": s.get("form"), "company": (s.get("display_names") or [""])[0], "date": s.get("file_date"),
                    "url": url, "excerpt": txt[max(0, i-300): i+300]})
    if out: json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    return res


# ------------------------------------------------------------------ Gerichtsentscheidungen (US, gemeinfrei)
def court(query, n=3):
    api = "https://www.courtlistener.com/api/rest/v4/search/?" + urllib.parse.urlencode({"q": query, "type": "o", "order_by": "score desc"})
    res = json.loads(_get(api)).get("results", [])[:n]
    return [{"case": r.get("caseName"), "court": r.get("court"), "date": r.get("dateFiled"),
             "url": "https://www.courtlistener.com" + (r.get("absolute_url") or ""), "snippet": _clean(" ".join(o.get("snippet", "") for o in r.get("opinions", [])))} for r in res]


# ------------------------------------------------------------------ Bildnachweise
def credits_text(img_dir, used=None):
    p = f"{img_dir}/credits.json"
    if not os.path.exists(p): return ""
    cr = [c for c in json.load(open(p)) if used is None or c["file"] in used]
    lines = ["Image credits:"] + [f"- {c['title'] or c['file']}: {c['author']} – {c['license']} – {c['source']} ({c['page']})" for c in cr]
    return "\n".join(lines)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "commons": print(json.dumps(commons(a[1], int(a[2]), a[3], person="--person" in a), indent=1, ensure_ascii=False))
    elif a[0] == "loc": print(json.dumps(loc(a[1], int(a[2]), a[3]), indent=1, ensure_ascii=False))
    elif a[0] == "nasa": print(json.dumps(nasa(a[1], int(a[2]), a[3]), indent=1, ensure_ascii=False))
    elif a[0] == "sec": print(json.dumps(sec(a[1], a[2], a[3] if len(a) > 3 else None), indent=1, ensure_ascii=False))
    elif a[0] == "court": print(json.dumps(court(a[1], int(a[2]) if len(a) > 2 else 3), indent=1, ensure_ascii=False))
    elif a[0] == "credits": print(credits_text(a[1]))
