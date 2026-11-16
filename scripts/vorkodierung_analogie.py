"""Wendet die Analogieregeln (scripts/analogieregeln.py) auf das Blatt 'zu_kodieren' an.

Füllt nur leere Zeilen; bereits manuell kodierte Zeilen bleiben unverändert.
Spalte 'quelle': 'Analogieregel R<n>' (Vorkodierung, von der Autorin zu prüfen) bzw. 'STREITIG'.
Alle Codes stammen aus den BA-Verzeichnissen; unbekannte Analogien führen zum Abbruch.
"""
import re, sys, csv
from pathlib import Path
import openpyxl
from openpyxl.styles import PatternFill

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from kodiere_beruf_auto import norm
from analogieregeln import REGELN, ENTSCHEIDUNGEN, EINZELFAELLE

alpha = {str(n): str(c) for n, c in openpyxl.load_workbook(
    ROOT / "codebook/quellen/Alphabetisches-Verzeichnis-Berufsbenennungen.xlsx", read_only=True
)["alphabet_Verz_Berufsb"].iter_rows(min_row=6, values_only=True) if n and c}
syst = {str(c): str(n) for c, n, *_ in openpyxl.load_workbook(
    ROOT / "codebook/quellen/Systematisches-Verzeichnis-KldB-2020.xlsx", read_only=True
)["Systematik_Langbezeichnungen"].iter_rows(min_row=6, values_only=True) if c}

def aufloesen(analogie):
    if analogie in ("WQ", "UNSPEZ") or analogie.startswith(("STREITIG", "BHG:")):
        return None
    if analogie.isdigit():
        if analogie not in syst: raise SystemExit(f"Code fehlt im Systematischen Verzeichnis: {analogie}")
        return analogie
    if analogie not in alpha: raise SystemExit(f"Analogie fehlt im Alphabetischen Verzeichnis: {analogie}")
    return alpha[analogie]

PRAEFIX = re.compile(r"^(junior(position|-position|-mitarbeiterin|-mitarbeiter| mitarbeiterin| mitarbeiter)?( (in der|im bereich|in|im|für|bei|als))?[\s-]|"
                     r"(berufs|direkt|quer)?einstieg (in die|in den|in der|in einer|in einem|im|als|in)\s|"
                     r"tätigkeit (in der|in den|im|als|in)\s|"
                     r"(projekt)?mitarbeit(er|erin)? (in der|in einer|in einem|in den|im|in|bei einem|bei einer|bei|an|für)\s(dem\s)?)")

def schluesseltext(titel):
    t = norm(titel)
    for _ in range(3):
        t2 = PRAEFIX.sub("", t)
        if t2 == t: break
        t = t2
    return t

regeln = [(i + 1, re.compile(m), a, k, aufloesen(a)) for i, (m, a, k) in enumerate(REGELN)]
entsch = {g: [(re.compile(m), a, aufloesen(a)) for m, a in lst] for g, lst in ENTSCHEIDUNGEN.items()}
blau = PatternFill("solid", fgColor="DDEBF7")
einzel = [(re.compile(m), a, aufloesen(a)) for m, a in EINZELFAELLE]

def schreibe(r, a, code, notiz, quelle, farbe):
    if a == "WQ": ws[f"H{r}"] = "x"
    elif a == "UNSPEZ": ws[f"H{r}"] = "u"
    elif a.startswith("BHG:"): ws[f"F{r}"] = a[4:]
    else: ws[f"F{r}"] = code[:2]; ws[f"G{r}"] = int(code[4])
    ws[f"I{r}"] = notiz; ws[f"J{r}"] = quelle
    for c in "FGH": ws[f"{c}{r}"].fill = farbe

f = ROOT / "codebook/kodierblatt_beruf.xlsx"
wb = openpyxl.load_workbook(f); ws = wb["zu_kodieren"]
if ws["J1"].value != "quelle": ws["J1"] = "quelle"
orange = PatternFill("solid", fgColor="F8CBAD"); gruen = PatternFill("solid", fgColor="E2EFDA")
stat = {"regel": 0, "entscheidung": 0, "streitig": 0, "offen": 0, "manuell": 0}
keine = PatternFill(fill_type=None); gelb = PatternFill("solid", fgColor="FFF2CC")
for r in range(2, ws.max_row + 1):          # frühere Vorkodierung zurücksetzen (idempotent)
    q = ws[f"J{r}"].value or ""
    if q.startswith(("Analogieregel", "Entscheidung")) or q == "STREITIG":
        for c in "FGHIJ": ws[f"{c}{r}"] = None
        for c in "ABI": ws[f"{c}{r}"].fill = keine
        for c in "FGH": ws[f"{c}{r}"].fill = gelb
for r in range(2, ws.max_row + 1):
    if ws[f"F{r}"].value or ws[f"H{r}"].value:
        if ws[f"J{r}"].value is None: ws[f"J{r}"] = "Autorin"
        stat["manuell"] += 1; continue
    t = schluesseltext(ws[f"B{r}"].value)
    treffer = next(((n, a, k, c) for n, rx, a, k, c in regeln if rx.match(t)), None)
    if not treffer:
        e = next(((rx, a2, c2) for rx, a2, c2 in einzel if rx.match(t)), None)
        if e:
            rx, a2, c2 = e
            schreibe(r, a2, c2, f"Einzelfall: analog '{a2}'" + (f" ({c2})" if c2 else ""), "Entscheidung Autorin (Einzelfall)", blau)
            stat["entscheidung"] += 1
        else:
            stat["offen"] += 1
        continue
    n, a, k, code = treffer
    if a == "WQ":
        schreibe(r, a, None, f"R{n}: {k}", f"Analogieregel R{n}", gruen)
        stat["regel"] += 1
    elif a.startswith("STREITIG"):
        g = a.split(":", 1)[1]
        unter = next(((rx, a2, c2) for rx, a2, c2 in entsch.get(g, []) if rx.search(t)), None)
        if unter:
            rx, a2, c2 = unter
            name = (syst[c2] if a2.isdigit() else a2) if c2 else a2
            schreibe(r, a2, c2, f"Gruppe {g}: analog '{name}'" + (f" ({c2})" if c2 else ""),
                     f"Entscheidung Autorin ({g})", blau)
            stat["entscheidung"] += 1
        else:
            ws[f"I{r}"] = f"{a} ({k})"; ws[f"J{r}"] = "STREITIG"
            for c in "ABFGHI": ws[f"{c}{r}"].fill = orange
            stat["streitig"] += 1
    else:
        name = syst[code] if a.isdigit() else a
        schreibe(r, a, code, f"R{n}: analog '{name}' ({code})" + (f"; {k}" if k else ""), f"Analogieregel R{n}", gruen)
        stat["regel"] += 1
from openpyxl.worksheet.datavalidation import DataValidation
for dv in list(ws.data_validations.dataValidation):
    if "H2" in str(dv.sqref): ws.data_validations.dataValidation.remove(dv)
dv = DataValidation(type="list", formula1='"x,u"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"H2:H{ws.max_row}")
ws["H1"] = "WQ (x) / UNSPEZ (u)"
# Spalte K: Beruf genannt vs. nur Tätigkeitsfeld (Regel 4) -> Sensitivitätsanalyse
FELD_START = re.compile(r"^(projekt)?mitarbeit(er|erin)?\b|^(tätigkeit|berufseinstieg|einstieg|direkteinstieg|quereinstieg) (in|im)\b")
FELD_WORT = re.compile(r"^((ambulante|stationäre|betriebliches|allgemeiner|sozialpädagogische|klinische|technische|psychosoziale)\s)?"
                       r"(oder (ambulante|stationäre) )?\S*(ung|wesen|hilfe|hilfen|arbeit|forschung|management|lektorat|dienst|"
                       r"bereich|sektor|programm|kommunikation|marketing|redaktion|controlling|research|affairs|bildung|"
                       r"studien|förderung|planung|leitung|kontrolle|sicherung|journalismus|bioinformatik|prüfung|"
                       r"recruiting|copywriting|it-sicherheit|it-security|engineering|entwicklung|beratung|f&e)\b")
ws["K1"] = "analogie_typ"
for r in range(2, ws.max_row + 1):
    q = ws[f"J{r}"].value or ""
    if ws[f"H{r}"].value in ("x", "u"):
        ws[f"K{r}"] = None; continue
    t_orig = norm(ws[f"B{r}"].value)
    ws[f"K{r}"] = "Taetigkeitsfeld" if (FELD_START.match(t_orig) or FELD_WORT.match(schluesseltext(ws[f"B{r}"].value))) else "Beruf"
ws.column_dimensions["K"].width = 16
ws.column_dimensions["J"].width = 20; ws.column_dimensions["I"].width = 70
wb.save(f)
print(stat)
