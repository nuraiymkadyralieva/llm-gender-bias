"""Führt automatische und manuelle/regelbasierte Kodierung zu codebook/beruf_codes.csv zusammen.

Eine Zeile je eindeutigem Empfehlungstitel (Szenario Beruf):
kategorie = BERUF | WQ | UNSPEZ; bhg (2-Steller); niveau (1-4); code5 (falls bekannt);
quelle (BA exakt | Analogieregel | Entscheidung Autorin); analogie_typ (Beruf | Taetigkeitsfeld).
"""
import csv, re
from pathlib import Path
import openpyxl
ROOT = Path(__file__).resolve().parent.parent

aus = []
for a in csv.DictReader(open(ROOT / "codebook/beruf_auto.csv", encoding="utf-8")):
    if a["typ"] == "eindeutig":
        c = a["code"]
        aus.append(dict(empfehlung=a["empfehlung"], kategorie="BERUF", bhg=c[:2], niveau=c[4], code5=c,
                        quelle="BA exakt", analogie_typ="Beruf"))
    elif a["typ"] == "weiterqualifikation":
        aus.append(dict(empfehlung=a["empfehlung"], kategorie="WQ", bhg="", niveau="", code5="",
                        quelle="Regel 3 (automatisch)", analogie_typ=""))
ws = openpyxl.load_workbook(ROOT / "codebook/kodierblatt_beruf.xlsx", read_only=True)["zu_kodieren"]
for r in ws.iter_rows(min_row=2, values_only=True):
    kern, emp, n, typ, vor, bhg, niv, wq, notiz, quelle, atyp = r[:11]
    kat = "WQ" if wq == "x" else "UNSPEZ" if wq == "u" else "BERUF"
    m = re.search(r"\((\d{5})\)", notiz or "")
    aus.append(dict(empfehlung=emp, kategorie=kat, bhg=bhg or "", niveau=niv or "", code5=m.group(1) if m else "",
                    quelle=quelle or "", analogie_typ=atyp or ""))
fehlend = [a["empfehlung"] for a in aus if a["kategorie"] == "BERUF" and not a["bhg"]]
assert not fehlend, f"ohne BHG: {fehlend[:5]}"
with open(ROOT / "codebook/beruf_codes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(aus[0])); w.writeheader(); w.writerows(aus)
rec = list(csv.DictReader(open(ROOT / "data/processed/recommendations.csv", encoding="utf-8")))
idx = {a["empfehlung"]: a for a in aus}
beruf = [x for x in rec if x["scenario"] == "beruf"]
ohne = [x["empfehlung"] for x in beruf if x["empfehlung"] not in idx]
print(f"{len(aus)} Titel kodiert; Empfehlungen Beruf: {len(beruf)}, ohne Code: {len(ohne)}")
from collections import Counter
print(Counter(idx[x["empfehlung"]]["kategorie"] for x in beruf if x["empfehlung"] in idx))
print(Counter(idx[x["empfehlung"]]["analogie_typ"] for x in beruf if x["empfehlung"] in idx))
