"""Automatische Kodierung der Studienempfehlungen nach der Destatis-Fächersystematik
(Schlüsselverzeichnis WS 2026/27, Abschnitt 4.1). Regelbasiert, kein LLM.
Ausgabe: codebook/studium_auto.csv (ein Eintrag je eindeutigem Titel).
"""
import csv, re, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def norm(s):
    s = (s or "").lower().replace("–", "-")
    s = re.sub(r"\((b\.\s?sc\.|b\.\s?a\.|m\.\s?sc\.|b\.\s?eng\.|staatsexamen)\)", "", s)
    return re.sub(r"\s+", " ", s).strip(" .,-")

def kern(t):
    k = re.sub(r"\s*\([^)]*\)", "", t)
    k = re.split(r"\s+(?:oder|bzw\.?|und/oder|mit|im|in)\s+|\s/\s|,|;|:|\s-\s", k)[0]
    return k.strip(" .")

def lexikon():
    lex = collections.defaultdict(set)
    for r in csv.DictReader(open(ROOT / "codebook/quellen/destatis_faecher.csv", encoding="utf-8")):
        name = norm(r["studienfach"])
        varianten = {name, re.sub(r"\s*\([^)]*\)", "", name)}
        varianten |= {v.strip() for v in re.sub(r"\s*\([^)]*\)", "", name).split("/") if len(v.strip()) > 3}
        for v in varianten:
            lex[v].add((r["fach_schluessel"], r["studienbereich"]))
    return lex

def main():
    lex = lexikon()
    rows = [r for r in csv.DictReader(open(ROOT / "data/processed/recommendations.csv", encoding="utf-8"))
            if r["scenario"] == "studienwahl"]
    haeuf = collections.Counter(r["empfehlung"] for r in rows)
    aus = []
    for titel, n in haeuf.most_common():
        t = norm(titel); e = {"empfehlung": titel, "anzahl": n, "schluessel": "", "fach": "", "studienbereich": "", "typ": "kein_treffer"}
        for k in (t, kern(t)):
            if k in lex:
                tr = sorted(lex[k]); stbs = {s for _, s in tr}
                e.update(schluessel=k, fach="|".join(f for f, _ in tr), studienbereich="|".join(sorted(stbs)),
                         typ="eindeutig" if len(stbs) == 1 else "mehrdeutig")
                break
        aus.append(e)
    with open(ROOT / "codebook/studium_auto.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(aus[0])); w.writeheader(); w.writerows(aus)
    g = sum(haeuf.values())
    for typ in ("eindeutig", "mehrdeutig", "kein_treffer"):
        s = [a for a in aus if a["typ"] == typ]
        print(f"{typ:13s} {len(s):4d} Titel {sum(a['anzahl'] for a in s)/g:6.1%}")

if __name__ == "__main__":
    main()
