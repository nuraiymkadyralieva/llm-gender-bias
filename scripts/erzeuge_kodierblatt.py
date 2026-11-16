"""Erzeugt codebook/kodierblatt_beruf.xlsx für die manuelle Kodierung (Szenario Beruf).

Blatt 'zu_kodieren': alle Titel ohne eindeutigen automatischen Treffer, nach Kern sortiert
  -> Spalten BHG (2-Steller) und Niveau (1-4) manuell ausfüllen.
Blatt 'pruefung_auto': Zufallsstichprobe (n=50, Seed 2026) automatisch kodierter Titel
  -> Spalte 'korrekt' (ja/nein) zur Prüfung der Kodiergüte.
Blätter 'BHG' und 'Niveau': Referenz aus dem Systematischen Verzeichnis der KldB 2010 (Fassung 2020).
"""
import csv, random, sys
from pathlib import Path
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from kodiere_beruf_auto import kandidaten

auto = list(csv.DictReader(open(ROOT / "codebook/beruf_auto.csv", encoding="utf-8")))
sysv = openpyxl.load_workbook(ROOT / "codebook/quellen/Systematisches-Verzeichnis-KldB-2020.xlsx", read_only=True)
bhg = [(str(c), str(n)) for c, n, *_ in sysv["Systematik_Langbezeichnungen"].iter_rows(min_row=6, values_only=True)
       if c and len(str(c)) == 2]

wb = openpyxl.Workbook()
fett = Font(bold=True); gelb = PatternFill("solid", fgColor="FFF2CC")

# Blatt 1: manuell
ws = wb.active; ws.title = "zu_kodieren"
kopf = ["kern", "empfehlung", "anzahl", "auto_typ", "auto_vorschlag", "BHG", "Niveau", "WQ", "notiz"]
ws.append(kopf)
offen = [a for a in auto if a["typ"] != "eindeutig" and a["typ"] != "weiterqualifikation"]
offen.sort(key=lambda a: (kandidaten(a["empfehlung"])[1][-1][1], -int(a["anzahl"])))
for a in offen:
    ws.append([kandidaten(a["empfehlung"])[1][-1][1], a["empfehlung"], int(a["anzahl"]), a["typ"], a["code"], None, None, None, None])
dv_bhg = DataValidation(type="list", formula1="=BHG!$A$2:$A$%d" % (len(bhg) + 1), allow_blank=True)
dv_niv = DataValidation(type="list", formula1='"1,2,3,4"', allow_blank=True)
dv_wq = DataValidation(type="list", formula1='"x"', allow_blank=True)
for dv, col in ((dv_bhg, "F"), (dv_niv, "G"), (dv_wq, "H")):
    ws.add_data_validation(dv); dv.add(f"{col}2:{col}{len(offen)+1}")
    for r in range(2, len(offen) + 2): ws[f"{col}{r}"].fill = gelb

# Blatt 2: Prüfstichprobe
wp = wb.create_sheet("pruefung_auto")
wp.append(["empfehlung", "anzahl", "schluessel", "code_auto", "BHG_auto", "Niveau_auto", "korrekt (ja/nein)", "notiz"])
random.seed(2026)
for a in random.sample([a for a in auto if a["typ"] == "eindeutig"], 50):
    wp.append([a["empfehlung"], int(a["anzahl"]), a["schluessel"], a["code"], a["code"][:2], a["code"][4], None, None])
for r in range(2, 52): wp[f"G{r}"].fill = gelb

# Referenzblätter
wr = wb.create_sheet("BHG"); wr.append(["BHG", "Berufshauptgruppe (KldB 2010, Fassung 2020)"])
for c, n in bhg: wr.append([c, n])
wn = wb.create_sheet("Niveau"); wn.append(["Niveau", "Anforderungsniveau (5. Stelle)"])
for row in [(1, "Helfer-/Anlerntätigkeiten"), (2, "fachlich ausgerichtete Tätigkeiten"),
            (3, "komplexe Spezialistentätigkeiten"), (4, "hoch komplexe Tätigkeiten (Experten)")]:
    wn.append(row)

for s, breiten in ((ws, [28, 70, 8, 18, 14, 7, 7, 5, 40]), (wp, [70, 8, 28, 10, 9, 11, 16, 40]), (wr, [6, 80]), (wn, [7, 45])):
    for i, b in enumerate(breiten): s.column_dimensions[chr(65 + i)].width = b
    for c in s[1]: c.font = fett
    s.freeze_panes = "A2"

ziel = ROOT / "codebook/kodierblatt_beruf.xlsx"
wb.save(ziel)
print(f"{len(offen)} Titel zu kodieren ({sum(int(a['anzahl']) for a in offen)} Empfehlungen), 50 Prüffälle -> {ziel.relative_to(ROOT)}")
print(len(bhg), "Berufshauptgruppen")
