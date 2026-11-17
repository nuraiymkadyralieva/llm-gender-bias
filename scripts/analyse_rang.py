"""FF1: Rangpositionen. Unterscheidet sich die Platzierung derselben Empfehlung
zwischen den Varianten?

Analyseeinheit ist wie in Abschnitt 4.5 das Profil: Je Profil, Modell und
Variantenpaar wird zuerst die mittlere Rangdifferenz ueber alle Codes gebildet,
die in beiden Varianten vorkommen; getestet wird anschliessend ueber die Profile.
Nur Codes, die in beiden verglichenen Varianten mindestens einmal vorkommen.

Die Kategorien WQ und UNSPEZ haben keinen fuenfstelligen Code; sie werden hier
ueber ihren Kategorienamen unterschieden, nicht zusammengefasst.
"""
import csv, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon
ROOT = Path(__file__).resolve().parent.parent
MODELLE = {"openai": "GPT-6.1", "anthropic": "Claude Sonnet 5.5", "google": "Gemini 4"}

b = {r["empfehlung"]: (r["code5"] or (f"BHG{r['bhg']}" if r["bhg"] else r["kategorie"])) for r in csv.DictReader(open(ROOT/"codebook/beruf_codes.csv", encoding="utf-8"))}
s = {r["empfehlung"]: (r["fach_schluessel"] or r["studienbereich"]) for r in csv.DictReader(open(ROOT/"codebook/studium_codes.csv", encoding="utf-8"))}
df = pd.read_csv(ROOT/"data/processed/recommendations.csv")
df["code"] = df["empfehlung"].map({**b, **s})

# mittlerer Rang je Profil x Modell x Variante x Code (nicht genannt = kein Eintrag)
mr = df.groupby(["model_key","scenario","profile_id","variant","code"])["rang"].mean().reset_index()
piv = mr.pivot_table(index=["model_key","scenario","profile_id","code"], columns="variant", values="rang")

zeilen = []
for mk, name in MODELLE.items():
    for a, bb in (("w","m"),("w","n"),("m","n")):
        sub = piv.loc[mk].dropna(subset=[a, bb])
        d_code = (sub[a] - sub[bb])
        # Analyseeinheit Profil: erst je Profil mitteln, dann ueber die Profile testen
        d_prof = d_code.groupby(level="profile_id").mean().values
        p = (wilcoxon(d_prof, zero_method="wilcox").pvalue
             if len(d_prof) > 5 and not np.allclose(d_prof, 0) else np.nan)
        zeilen.append(dict(modell=name, vergleich=f"{a}-{bb}", n_profile=len(d_prof), n_codes=len(d_code),
                           median=np.median(d_prof), mittel=d_prof.mean(),
                           anteil_abweichend=float((np.abs(d_code.values) > 0.2).mean()), p=p))
        if (a, bb) == ("w","m"):
            gr = sub.assign(d=sub[a]-sub[bb]).reset_index()
            gr = gr.reindex(gr.d.abs().sort_values(ascending=False).index).head(6)
            print(f"-- {name}: größte Rangunterschiede w-m")
            for _, r in gr.iterrows():
                print(f"   {r['profile_id']} {r['code']}: w {r[a]:.1f} vs m {r[bb]:.1f}  (Δ {r['d']:+.1f})")
t = pd.DataFrame(zeilen)
t.to_csv(ROOT/"results/tables/rang.csv", index=False, float_format="%.4f")
print(t.round(3).to_string(index=False))


# --- Übereinstimmung auf Rang 1 (in Abschnitt 4.4 angekündigt) ---------------------------------
import itertools
r1 = df[df["rang"] == 1].set_index(["model_key", "scenario", "profile_id", "variant", "repetition"])["code"]
zeilen1 = []
for (mk, sc, pid), g in r1.groupby(level=[0, 1, 2]):
    d = {v: [g.loc[(mk, sc, pid, v, r)] for r in range(1, 6)] for v in "wmn"}
    for a, b2 in (("w", "m"), ("w", "n"), ("m", "n")):
        zeilen1.append(dict(model_key=mk, scenario=sc, profile_id=pid, paar=f"{a}-{b2}",
                            innerhalb=np.mean([np.mean([x == y for x, y in itertools.combinations(d[v], 2)]) for v in (a, b2)]),
                            zwischen=np.mean([x == y for x in d[a] for y in d[b2]])))
r1t = pd.DataFrame(zeilen1)
r1t["D"] = r1t["innerhalb"] - r1t["zwischen"]
r1t.to_csv(ROOT / "results/tables/rang1.csv", index=False, float_format="%.4f")
print("\n-- Übereinstimmung auf Rang 1")
zeilen2 = []
for mk, name in MODELLE.items():
    for paar in ("w-m", "w-n", "m-n"):
        x = r1t[(r1t.paar == paar) & (r1t.model_key == mk)]
        d = x["D"].values
        nz = int((d != 0).sum())
        # exakter Test: bei wenigen von null verschiedenen Differenzen ist die
        # Normalapproximation nicht gueltig (kleinstes erreichbares p = 2/2**nz)
        try:
            p = wilcoxon(d, zero_method="wilcox", mode="exact").pvalue if nz else np.nan
        except ValueError:
            p = wilcoxon(d, zero_method="wilcox").pvalue if nz else np.nan
        zeilen2.append(dict(modell=name, paar=paar, n_profile=len(d), n_differenzen=nz,
                            innerhalb=x.innerhalb.mean(), zwischen=x.zwischen.mean(),
                            differenz=d.mean(), p_exakt=p))
        print(f"   {name:18s} {paar}  innerhalb {x.innerhalb.mean():.3f}  zwischen {x.zwischen.mean():.3f}  "
              f"Δ {x.D.mean():+.3f}  n≠0 {nz:2d}  p_exakt {p:.4f}")
pd.DataFrame(zeilen2).to_csv(ROOT / "results/tables/rang1_tests.csv", index=False, float_format="%.4f")
