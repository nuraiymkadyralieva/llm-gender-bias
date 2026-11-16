"""FF1: Rangpositionen. Unterscheidet sich die Platzierung derselben Empfehlung
zwischen den Varianten? Einheit: Profil x Modell x Code, gemittelt über Wiederholungen.
Nur Codes, die in beiden verglichenen Varianten mindestens einmal vorkommen.
"""
import csv, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon
ROOT = Path(__file__).resolve().parent.parent
MODELLE = {"openai": "GPT-6.1", "anthropic": "Claude Sonnet 5.5", "google": "Gemini 4"}

b = {r["empfehlung"]: (r["code5"] or f"BHG{r['bhg']}" or r["kategorie"]) for r in csv.DictReader(open(ROOT/"codebook/beruf_codes.csv", encoding="utf-8"))}
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
        d = (sub[a] - sub[bb]).values
        p = wilcoxon(d).pvalue if len(d) > 5 and not np.allclose(d, 0) else np.nan
        zeilen.append(dict(modell=name, vergleich=f"{a}-{b}" if False else f"{a}-{bb}", n_codes=len(d),
                           median=np.median(d), mittel=d.mean(), anteil_abweichend=float((np.abs(d) > 0.2).mean()), p=p))
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
for mk, name in MODELLE.items():
    for paar in ("w-m", "w-n", "m-n"):
        x = r1t[(r1t.paar == paar) & (r1t.model_key == mk)]
        p = wilcoxon(x["D"].values).pvalue if not np.allclose(x["D"].values, 0) else np.nan
        print(f"   {name:18s} {paar}  innerhalb {x.innerhalb.mean():.3f}  zwischen {x.zwischen.mean():.3f}  Δ {x.D.mean():+.3f}  p {p:.3f}")
