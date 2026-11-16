"""Automatische Vorkodierung der Berufsempfehlungen (Szenario Beruf) nach KldB 2010 (Fassung 2020).

Regelbasiert und reproduzierbar (kein LLM): Abgleich der Empfehlungstitel mit dem
'Alphabetischen Verzeichnis der Berufsbenennungen' der Bundesagentur für Arbeit.
Ausgabe: codebook/beruf_auto.csv (ein Eintrag pro eindeutigem Titel) zur manuellen Prüfung.
"""
import csv, re, collections
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
VERZ = ROOT / "codebook/quellen/Alphabetisches-Verzeichnis-Berufsbenennungen.xlsx"

WEITERQ = re.compile(r"^(master|masterstudium|m\.\s?sc|m\.\s?a\.|promotion|doktor|weiterbildung|"
                     r"ausbildung|zweitstudium|aufbaustudium|studium|weiterführendes studium|"
                     r"psychotherapeut\w*ausbildung)\b")
PRAEFIXE = re.compile(r"^(junior|senior|trainee|berufseinstieg als|einstieg als|einstieg in die|einstieg in den|"
                      r"einstieg in|einstieg im|tätigkeit als|tätigkeit in|arbeit als|position als|stelle als|"
                      r"quereinstieg als|quereinstieg in)\s+")


def norm(s):
    s = (s or "").lower().replace("–", "-").replace("­", "")
    s = re.sub(r"\(m/w/d\)|\(w/m/d\)", "", s)
    s = re.sub(r"[:*_/]-?innen\b|[:*_/]-?in\b|\(in\)|\(innen\)", "", s)   # Gender-Markierungen
    s = re.sub(r"(?<=\w)[/:*_]-?(r|e|n)\b", "", s)                                 # Wissenschaftliche/r, Angestellte/r
    s = re.sub(r"\b(\w+)(e|er|en) oder \1(e|er|en) (\w+?)(in)? oder \4\b", r"\1\2 \4", s)
    return re.sub(r"\s+", " ", s).strip(" .,-")


def schluessel(s):
    return re.sub(r"[\s-]+", "", s)        # "Business Analyst" == "Business-Analyst"


def lexikon():
    """Liefert zwei Nachschlagetabellen: 'voll' (vollständige Benennung) und
    'basis' (Benennung ohne Spezifikation nach ' - ' bzw. in Klammern; nur zur Prüfung)."""
    ws = openpyxl.load_workbook(VERZ, read_only=True)["alphabet_Verz_Berufsb"]
    lex = collections.defaultdict(set)
    basis = collections.defaultdict(set)
    for name, code in ws.iter_rows(min_row=6, values_only=True):
        if not name or not code or not str(code).isdigit():
            continue
        name = str(name)
        varianten = {name, re.sub(r"\s*\([^)]*\)", "", name)}
        abk = re.fullmatch(r".*\(([A-ZÄÖÜ]{2,6})\)", name)
        if abk:
            varianten.add(abk.group(1))
        for v in list(varianten):
            m = re.match(r"^(.*?)(/in|/-in)\b(.*)$", v)          # z. B. Sozialarbeiter/in
            if m:
                varianten |= {m.group(1) + m.group(3), m.group(1) + "in" + m.group(3)}
        for v in varianten:
            lex[schluessel(norm(v))].add(str(code))
            b = re.split(r"\s+-\s+|\s*\(", norm(v))[0]
            basis[schluessel(b)].add(str(code))
    return lex, basis


def kandidaten(titel):
    t = norm(titel)
    ks = [("exakt", t)]
    k = re.sub(r"\s*\([^)]*\)", "", t)
    k = re.split(r"\s+(?:oder|bzw\.?|und/oder|sowie)\s+|\s/\s|/|,|;|\s-\s|:", k)[0].strip(" .")
    ks.append(("kern", k))
    p = PRAEFIXE.sub("", k)
    ks.append(("ohne_praefix", p))
    o = re.split(r"\s+(?:in der|in den|in einem|in einer|im|in|bei|beim|an einer|an|für|mit|eines|einer|zur|zum)\s+", p)[0]
    ks.append(("ohne_zusatz", o))
    return t, ks


def main():
    lex, basis = lexikon()
    rows = [r for r in csv.DictReader(open(ROOT / "data/processed/recommendations.csv", encoding="utf-8"))
            if r["scenario"] == "beruf"]
    haeuf = collections.Counter(r["empfehlung"] for r in rows)
    aus = []
    for titel, n in haeuf.most_common():
        t, ks = kandidaten(titel)
        eintrag = {"empfehlung": titel, "anzahl": n, "abgleich": "", "schluessel": "", "code": "", "typ": "kein_treffer"}
        if WEITERQ.match(t):
            eintrag.update(typ="weiterqualifikation", code="WQ")
        else:
            for tabelle, stufe in ((lex, ""), (basis, "basis_")):
                treffer = next(((art, k) for art, k in ks if schluessel(k) in tabelle), None)
                if treffer:
                    art, k = treffer
                    codes = sorted(tabelle[schluessel(k)])
                    eintrag.update(abgleich=stufe + art, schluessel=k, code="|".join(codes),
                                   typ=("eindeutig" if len(codes) == 1 else "mehrdeutig")
                                       + ("_pruefen" if stufe else ""))
                    # 'Wissenschaftliche/r Mitarbeiter/in' ist in der KldB der Hochschulforschung (843)
                    # zugeordnet; bei Industrie-/Pharmaforschung daher manuell prüfen.
                    if k.startswith("wissenschaftliche") and eintrag["typ"] == "eindeutig":
                        eintrag["typ"] = "eindeutig_pruefen"
                    break
        aus.append(eintrag)
    ziel = ROOT / "codebook/beruf_auto.csv"
    with ziel.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(aus[0]) + ["code_final", "notiz"])
        w.writeheader(); w.writerows(aus)
    gesamt = sum(haeuf.values())
    print(f"{len(aus)} eindeutige Titel, {gesamt} Empfehlungen -> {ziel.relative_to(ROOT)}")
    for typ in ["eindeutig", "eindeutig_pruefen", "mehrdeutig", "mehrdeutig_pruefen", "weiterqualifikation", "kein_treffer"]:
        sel = [e for e in aus if e["typ"] == typ]
        print(f"  {typ:20s} {len(sel):4d} Titel  {sum(e['anzahl'] for e in sel)/gesamt:6.1%} der Empfehlungen")


if __name__ == "__main__":
    main()
