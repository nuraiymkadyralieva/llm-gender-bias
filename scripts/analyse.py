"""Auswertung des kontrafaktischen Audits (Kapitel 5).

Analyseeinheit: Profil x Modell (Wiederholungen werden gemittelt).
Kennzahlen:
  - Jaccard-Überschneidung der empfohlenen Codes zwischen Varianten (w/m/n), verglichen mit
    der Überschneidung zwischen Wiederholungen derselben Variante (Grundrauschen).
  - Mittlerer Frauenanteil F der empfohlenen Fächer/Berufe; ΔF = F_w - F_m.
  - MINT-Anteil (Studienwahl), Anforderungsniveau und WQ-Anteil (Beruf).
Tests: Wilcoxon-Vorzeichen-Rang-Test über Profile, Median-Differenz mit 95-%-Bootstrap-KI.
Explorativ, keine Korrektur für multiples Testen (wird im Text diskutiert).
Aufruf: python scripts/analyse.py [--ohne-feld]   (--ohne-feld: Sensitivitätsanalyse Beruf)
"""
import argparse, csv, itertools, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import wilcoxon
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
RNG = np.random.default_rng(2026)
MODELLE = {"openai": "GPT-6.1", "anthropic": "Claude Sonnet 5.5", "google": "Gemini 4"}
MINT_FG = {"Mathematik, Naturwissenschaften", "Ingenieurwissenschaften"}

# ---------- Codes und Referenzdaten ----------
def lade_studium():
    fa = {r["fach_schluessel"]: r for r in csv.DictReader(open(ROOT / "codebook/quellen/destatis_faecher_frauenanteil.csv", encoding="utf-8"))}
    stb = {r["studienbereich"]: float(r["frauenanteil"]) for r in csv.DictReader(open(ROOT / "codebook/quellen/destatis_studienbereich_frauenanteil.csv", encoding="utf-8")) if r["frauenanteil"]}
    m = {}
    for r in csv.DictReader(open(ROOT / "codebook/studium_codes.csv", encoding="utf-8")):
        k = r["fach_schluessel"]
        f = float(fa[k]["frauenanteil"]) if k and fa[k]["frauenanteil"] else stb.get(r["studienbereich"])
        m[r["empfehlung"]] = dict(fein=k or r["studienbereich"], grob=r["studienbereich"], frauenanteil=f,
                                  mint=float(r["faechergruppe"] in MINT_FG), niveau=np.nan, wq=0.0, feld=False)
    return m

def lade_frauenanteil_beruf():
    ws = openpyxl.load_workbook(ROOT / "codebook/quellen/bo-heft-d-0-202603-xlsx.xlsx", read_only=True)["SVB - Tabelle I"]
    fa = {}
    for r in ws.iter_rows(min_row=12, values_only=True):
        if r[0] and str(r[0])[:2].isdigit() and isinstance(r[1], (int, float)) and r[1] > 0:
            fa[str(r[0]).split()[0]] = r[3] / r[1]
    return fa

def lade_beruf():
    fa = lade_frauenanteil_beruf(); m = {}
    for r in csv.DictReader(open(ROOT / "codebook/beruf_codes.csv", encoding="utf-8")):
        kat, c5, bhg = r["kategorie"], r["code5"], r["bhg"]
        if kat == "BERUF":
            fein, grob = (c5 or f"BHG{bhg}"), f"BHG{bhg}"
            f = fa.get(c5[:4]) if c5 else None
            f = f if f is not None else fa.get(bhg)
        else:
            fein = grob = kat; f = None
        m[r["empfehlung"]] = dict(fein=fein, grob=grob, frauenanteil=f, mint=np.nan,
                                  niveau=float(r["niveau"]) if r["niveau"] else np.nan,
                                  wq=float(kat == "WQ"), feld=r["analogie_typ"] == "Taetigkeitsfeld")
    return m

# ---------- Statistik ----------
def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else np.nan

def boot_ci(d, n=10000):
    d = np.asarray(d, float); d = d[~np.isnan(d)]
    if len(d) == 0: return (np.nan, np.nan)
    s = RNG.choice(d, size=(n, len(d)), replace=True)
    return tuple(np.percentile(np.median(s, axis=1), [2.5, 97.5]))

def test(d):
    d = np.asarray(d, float); d = d[~np.isnan(d)]
    if len(d) < 3 or np.allclose(d, 0): return np.nan
    return wilcoxon(d, zero_method="wilcox").pvalue

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ohne-feld", action="store_true"); args = ap.parse_args()
    suffix = "_ohne_feld" if args.ohne_feld else ""
    rec = pd.read_csv(ROOT / "data/processed/recommendations.csv")
    attr = pd.DataFrame([{"empfehlung": k, "scenario": sz, **v}
                         for sz, d in (("studienwahl", lade_studium()), ("beruf", lade_beruf()))
                         for k, v in d.items()]).drop_duplicates(["empfehlung", "scenario"])
    df = rec.merge(attr, on=["empfehlung", "scenario"], how="left", validate="many_to_one")
    assert df["fein"].notna().all(), "Empfehlungen ohne Code"
    if args.ohne_feld:
        df = df[~((df["scenario"] == "beruf") & (df["feld"] == True))]

    keys = ["model_key", "scenario", "profile_id", "variant", "repetition"]
    pro_rep = df.groupby(keys).agg(F=("frauenanteil", "mean"), MINT=("mint", "mean"), Niveau=("niveau", "mean"),
                                   WQ=("wq", "mean"), fein=("fein", lambda s: frozenset(s)),
                                   grob=("grob", lambda s: frozenset(s))).reset_index()
    # Mittel über Wiederholungen
    pv = pro_rep.groupby(keys[:-1])[["F", "MINT", "Niveau", "WQ"]].mean().reset_index()
    pv.to_csv(ROOT / f"results/tables/kennzahlen_profil_variante{suffix}.csv", index=False)

    # Jaccard: zwischen Varianten vs. innerhalb Variante
    jz = []
    for (mk, sc, pid), g in pro_rep.groupby(keys[:3]):
        sets = {v: {e: list(gg[e]) for e in ("fein", "grob")} for v, gg in g.groupby("variant")}
        for ebene in ("fein", "grob"):
            within = {v: np.nanmean([jaccard(a, b) for a, b in itertools.combinations(sets[v][ebene], 2)]) for v in sets}
            for v1, v2 in (("w", "m"), ("w", "n"), ("m", "n")):
                between = np.nanmean([jaccard(a, b) for a in sets[v1][ebene] for b in sets[v2][ebene]])
                jz.append(dict(model_key=mk, scenario=sc, profile_id=pid, ebene=ebene, paar=f"{v1}-{v2}",
                               J_innerhalb=(within[v1] + within[v2]) / 2, J_zwischen=between))
    jz = pd.DataFrame(jz); jz["D_J"] = jz["J_innerhalb"] - jz["J_zwischen"]
    jz.to_csv(ROOT / f"results/tables/jaccard{suffix}.csv", index=False)

    # Tests
    wide = pv.pivot_table(index=["model_key", "scenario", "profile_id"], columns="variant", values=["F", "MINT", "Niveau", "WQ"])
    zeilen = []
    def eintrag(model, szen, kennzahl, paar, d, extra=None):
        d = np.asarray(d, float); ci = boot_ci(d)
        zeilen.append(dict(modell=MODELLE.get(model, model), szenario=szen, kennzahl=kennzahl, vergleich=paar, n=int(np.sum(~np.isnan(d))),
                           median=np.nanmedian(d), mittel=np.nanmean(d), ki_unten=ci[0], ki_oben=ci[1], p_wilcoxon=test(d), **(extra or {})))
    for mk in MODELLE:
        for szen, kennz in (("beide", ["F"]), ("studienwahl", ["F", "MINT"]), ("beruf", ["F", "Niveau", "WQ"])):
            sub = wide.loc[mk] if szen == "beide" else wide.loc[(mk, szen)]
            for k in kennz:
                for a, b in (("w", "m"), ("w", "n"), ("m", "n")):
                    eintrag(mk, szen, f"Δ{k}", f"{a}-{b}", (sub[(k, a)] - sub[(k, b)]).values)
        for ebene in ("fein", "grob"):
            for paar in ("w-m", "w-n", "m-n"):
                for szen in ("beide", "studienwahl", "beruf"):
                    s = jz[(jz.model_key == mk) & (jz.ebene == ebene) & (jz.paar == paar)]
                    if szen != "beide": s = s[s.scenario == szen]
                    eintrag(mk, szen, f"D_J ({ebene})", f"innerhalb-zwischen ({paar})", s["D_J"].values,
                            dict(J_innerhalb_mittel=s["J_innerhalb"].mean(), J_zwischen_mittel=s["J_zwischen"].mean()))
    tests = pd.DataFrame(zeilen)
    # Holm-Korrektur innerhalb der konfirmatorischen Hauptfamilie (ΔF, w-m, beide Szenarien, 3 Modelle)
    haupt = (tests.kennzahl == "ΔF") & (tests.vergleich == "w-m") & (tests.szenario == "beide")
    pw = tests.loc[haupt, "p_wilcoxon"].values; k = len(pw); hol = np.empty(k); lauf = 0.0
    for i, idx in enumerate(np.argsort(pw)):
        lauf = max(lauf, (k - i) * pw[idx]); hol[idx] = min(lauf, 1.0)
    tests["p_holm"] = np.nan; tests.loc[haupt, "p_holm"] = hol
    tests.to_csv(ROOT / f"results/tables/tests{suffix}.csv", index=False, float_format="%.4f")
    with pd.option_context("display.width", 200, "display.max_rows", 500, "display.float_format", "{:.3f}".format):
        print(tests[tests.vergleich.isin(["w-m", "innerhalb-zwischen (w-m)"])].drop(columns=["vergleich"]).to_string(index=False))

if __name__ == "__main__":
    main()
