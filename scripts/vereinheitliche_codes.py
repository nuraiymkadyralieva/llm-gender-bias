"""Regel 7: Vereinheitlichung von Empfehlungen, die dieselben Taetigkeiten nennen.

Regel 2 kodiert die zuerst genannte Option. Nennt eine Empfehlung mehrere Taetigkeiten
in einer Aufzaehlung, entscheidet damit die Reihenfolge ueber den Code, obwohl sie
inhaltlich beliebig ist. Regel 7 hebt das auf: Innerhalb eines Profils erhalten
Empfehlungen, die dieselben Taetigkeiten nennen, denselben Code.

Die betroffenen Faelle wurden gefunden, indem die Titel je Profil auf ihre Wortmenge
normalisiert und Gruppen mit mehr als einem Code ausgegeben wurden; jede Gruppe wurde
anschliessend von Hand geprueft. Das Ergebnis steht vollstaendig in
codebook/vereinheitlichung.csv und wird hier auf codebook/beruf_codes.csv angewandt.

Laeuft nach finalisiere_beruf.py und ist wiederholbar: bereits vereinheitlichte
Eintraege bleiben unveraendert.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODES = ROOT / "codebook/beruf_codes.csv"
REGEL = ROOT / "codebook/vereinheitlichung.csv"


def main():
    um = {}
    for r in csv.DictReader(REGEL.open(encoding="utf-8")):
        um[r["empfehlung"]] = (r["kategorie_neu"], r["code_neu"])

    zeilen = list(csv.DictReader(CODES.open(encoding="utf-8")))
    felder = list(zeilen[0].keys())
    geaendert = 0
    for z in zeilen:
        if z["empfehlung"] not in um:
            continue
        kat, c5 = um[z["empfehlung"]]
        if (z["kategorie"], z["code5"]) == (kat, c5):
            continue
        z["kategorie"] = kat
        z["code5"] = c5
        z["bhg"] = c5[:2] if c5 else ""
        z["niveau"] = c5[4] if len(c5) == 5 else ""
        z["quelle"] = "Regel 7 (vereinheitlicht)"
        geaendert += 1

    with CODES.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=felder)
        w.writeheader()
        w.writerows(zeilen)
    print(f"{geaendert} Titel nach Regel 7 vereinheitlicht ({len(um)} in der Regeltabelle).")


if __name__ == "__main__":
    main()
