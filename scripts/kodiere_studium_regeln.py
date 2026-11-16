"""Wendet Analogieregeln auf nicht automatisch kodierte Studienempfehlungen an
und schreibt codebook/studium_codes.csv (alle Titel; STREITIG-Fälle markiert)."""
import csv, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from kodiere_studium_auto import norm, kern
from analogieregeln_studium import REGELN
from analogieregeln_studium import ENTSCHEIDUNGEN, LEHRAMT_FAECHER, LEHRAMT_OHNE_FACH
LEHRAMT_RX = re.compile(r"\b(" + "|".join(LEHRAMT_FAECHER) + r")")
F = {r["studienfach"]: r for r in csv.DictReader(open(ROOT / "codebook/quellen/destatis_faecher.csv", encoding="utf-8"))}
for _, a, _ in REGELN:
    if not a.startswith("STREITIG") and a not in F: raise SystemExit(f"Fach fehlt: {a}")
for a in list(LEHRAMT_FAECHER.values()) + [a for _, a in LEHRAMT_OHNE_FACH]:
    if a not in F: raise SystemExit(f"Fach fehlt: {a}")
for g, lst in ENTSCHEIDUNGEN.items():
    for _, a in lst:
        if a not in F and a not in ("UNSPEZ",): raise SystemExit(f"Fach fehlt: {a}")
aus, offen, streit = [], [], {}
for a in csv.DictReader(open(ROOT / "codebook/studium_auto.csv", encoding="utf-8")):
    t = norm(a["empfehlung"]); k = kern(t)
    e = dict(empfehlung=a["empfehlung"], anzahl=a["anzahl"], fach_schluessel="", studienfach="", studienbereich="", faechergruppe="", quelle="", notiz="")
    def setze(fach, quelle, notiz=""):
        r = F[fach]; e.update(fach_schluessel=r["fach_schluessel"], studienfach=fach, studienbereich=r["studienbereich"],
                              faechergruppe=r["faechergruppe"], quelle=quelle, notiz=notiz)
    if a["typ"] == "eindeutig":
        fach = next(r["studienfach"] for r in F.values() if r["fach_schluessel"] == a["fach"].split("|")[0])
        setze(fach, "Destatis exakt")
    else:
        tr = next(((i + 1, rx, an, ko) for i, (rx, an, ko) in enumerate(REGELN) if re.match(rx, k) or re.match(rx, t)), None)
        if not tr: offen.append(a["empfehlung"]); e["quelle"] = "OFFEN"
        else:
            n, rx, an, ko = tr
            if an.startswith("STREITIG"):
                g = an.split(":")[1]
                ent = next(((rx2, a2) for rx2, a2 in ENTSCHEIDUNGEN.get(g, []) if re.search(rx2, t)), None)
                if g == "lehramt":
                    m = LEHRAMT_RX.search(t)   # erstes (linkestes) genanntes Fach
                    ent = ("", LEHRAMT_FAECHER[m.group(1)]) if m else next((x for x in LEHRAMT_OHNE_FACH if re.search(x[0], t)), None)
                if ent and ent[1] == "UNSPEZ": e.update(quelle=f"Entscheidung Autorin ({g})", studienbereich="UNSPEZ")
                elif ent: setze(ent[1], f"Entscheidung Autorin ({g})")
                else: e.update(quelle="STREITIG", notiz=g); streit.setdefault(g, []).append(a["empfehlung"])
            else: setze(an, f"Analogieregel S{n}", ko)
    aus.append(e)
with open(ROOT / "codebook/studium_codes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(aus[0])); w.writeheader(); w.writerows(aus)
from collections import Counter
print(Counter(x["quelle"].split(" (")[0].split(" S")[0] for x in aus))
print("OFFEN:", offen)
for g, l in streit.items(): print("STREITIG", g, len(l), l[:6])
