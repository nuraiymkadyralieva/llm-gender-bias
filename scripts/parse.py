"""Zerlegt die Rohantworten in eine Tabelle mit einer Zeile pro Empfehlung.

Eingabe:  data/raw/responses.jsonl (wird nie veraendert)
Ausgabe:  data/processed/recommendations.csv  - gueltige Empfehlungen
          data/processed/parse_issues.csv     - Antworten, die nicht dem Format entsprechen

Aufruf:   python scripts/parse.py [--in data/raw/pilot.jsonl]
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPALTEN = ["run_id", "timestamp", "model_key", "model_returned", "profile_id", "scenario",
           "variant", "typ", "repetition", "rang", "empfehlung", "titel_norm", "begruendung"]


def json_aus_text(text):
    """Holt das JSON-Array aus der Antwort, auch wenn es in ```json ... ``` steht."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    start, ende = text.find("["), text.rfind("]")
    if start == -1 or ende == -1:
        raise ValueError("kein JSON-Array gefunden")
    return json.loads(text[start:ende + 1])


def normalisieren(titel):
    """Einheitliche Schreibweise fuer die Kodiertabelle (Kleinschreibung, Leerzeichen).
    Geschlechtsspezifische Formen (z. B. 'Psychologin'/'Psychologe') bleiben bewusst
    erhalten; sie werden erst ueber die Kodiertabelle demselben Code zugeordnet.
    Vergleiche zwischen Varianten erfolgen daher immer auf Code-Ebene, nie auf Titel-Ebene."""
    t = titel.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t.strip(" .;:")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="eingabe", default="data/raw/responses.jsonl")
    args = ap.parse_args()

    # Pro (Modell, Prompt, Wiederholung) zählt der letzte vollständige Datensatz;
    # abgeschnittene Versuche (finish_reason "length"), die später wiederholt wurden, entfallen.
    datensaetze = {}
    for roh in (ROOT / args.eingabe).read_text(encoding="utf-8").splitlines():
        if not roh.strip():
            continue
        d = json.loads(roh)
        k = (d["model_key"], d["prompt_id"], d["repetition"])
        vollstaendig = d.get("status") == "ok" and d.get("finish_reason") != "length"
        if k not in datensaetze or vollstaendig or not datensaetze[k][1]:
            datensaetze[k] = (d, vollstaendig)

    zeilen, probleme = [], []
    for d, vollstaendig in datensaetze.values():
        if d.get("status") == "ok" and not vollstaendig:
            probleme.append({**{k: d.get(k) for k in SPALTEN if k in d},
                             "problem": "abgeschnitten (finish_reason length)"})
            continue
        basis = {k: d.get(k) for k in SPALTEN if k in d}
        if d.get("status") != "ok":
            probleme.append({**basis, "problem": "API-Fehler: " + str(d.get("error"))[:200]})
            continue
        try:
            liste = json_aus_text(d.get("response_text") or "")
            if len(liste) != 5:
                probleme.append({**basis, "problem": f"{len(liste)} statt 5 Empfehlungen"})
            for i, e in enumerate(liste, start=1):
                zeilen.append({**basis,
                               "rang": e.get("rang", i),
                               "empfehlung": e.get("empfehlung", ""),
                               "titel_norm": normalisieren(e.get("empfehlung", "")),
                               "begruendung": e.get("begruendung", "")})
        except (ValueError, json.JSONDecodeError, AttributeError) as ex:
            probleme.append({**basis, "problem": f"Format: {ex}"})

    aus = ROOT / "data/processed"
    aus.mkdir(parents=True, exist_ok=True)
    with (aus / "recommendations.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN, extrasaction="ignore")
        w.writeheader()
        w.writerows(zeilen)
    with (aus / "parse_issues.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN[:9] + ["problem"], extrasaction="ignore")
        w.writeheader()
        w.writerows(probleme)

    titel = {z["titel_norm"] for z in zeilen}
    print(f"{len(zeilen)} Empfehlungen, {len(titel)} eindeutige Titel, {len(probleme)} Problemfaelle")


if __name__ == "__main__":
    main()
