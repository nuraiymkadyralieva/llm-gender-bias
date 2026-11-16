"""Erzeugt bzw. ergaenzt die Kodiertabelle codebook/title_to_code.csv.

Jeder eindeutige (normalisierte) Titel erscheint genau einmal. Bereits kodierte
Zeilen bleiben erhalten; neue Titel werden mit leeren Code-Feldern angehaengt.
Die Spalten code, system, mint, quelle werden manuell ausgefuellt
(KldB 2010 ueber das Alphabetische Verzeichnis der Berufsbenennungen bzw.
Destatis-Faechersystematik). Die Variante (w/m/n) ist hier nicht sichtbar.

Aufruf:  python scripts/make_codebook.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPALTEN = ["titel_norm", "scenario", "anzahl", "code", "system", "mint", "quelle", "notiz"]


def main():
    zaehler = {}
    with (ROOT / "data/processed/recommendations.csv").open(encoding="utf-8") as f:
        for z in csv.DictReader(f):
            key = (z["titel_norm"], z["scenario"])
            zaehler[key] = zaehler.get(key, 0) + 1

    ziel = ROOT / "codebook/title_to_code.csv"
    vorhanden = {}
    if ziel.exists():
        with ziel.open(encoding="utf-8") as f:
            for z in csv.DictReader(f):
                vorhanden[(z["titel_norm"], z["scenario"])] = z

    for key, n in zaehler.items():
        zeile = vorhanden.get(key, {s: "" for s in SPALTEN})
        zeile.update({"titel_norm": key[0], "scenario": key[1], "anzahl": n})
        vorhanden[key] = zeile

    with ziel.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN)
        w.writeheader()
        for key in sorted(vorhanden):
            w.writerow(vorhanden[key])
    offen = sum(1 for z in vorhanden.values() if not z.get("code"))
    print(f"{len(vorhanden)} eindeutige Titel, davon {offen} noch nicht kodiert")


if __name__ == "__main__":
    main()
