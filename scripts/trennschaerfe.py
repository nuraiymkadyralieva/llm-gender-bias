"""Trennschärfe (statistische Power) des Designs, geschätzt per Resampling.

Grundlage ist die beobachtete Streuung der profilweisen ΔF-Werte (weiblich − männlich).
Für eine angenommene systematische Verschiebung δ werden 5.000 Stichproben zu je 20 Profilen
gezogen (Bootstrap aus den zentrierten Beobachtungen, plus δ) und mit dem Wilcoxon-Test geprüft.
Ausgegeben wird der Anteil der Stichproben mit p < 0,05.
"""
import numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon
ROOT = Path(__file__).resolve().parent.parent
MODELLE = {"openai": "GPT-6.1", "anthropic": "Claude Sonnet 5.5", "google": "Gemini 4"}
rng = np.random.default_rng(2026)
N = 5000

pv = pd.read_csv(ROOT / "results/tables/kennzahlen_profil_variante.csv")
w = pv.pivot_table(index=["model_key", "scenario", "profile_id"], columns="variant", values="F")
zeilen = []
for mk, name in MODELLE.items():
    d = ((w["w"] - w["m"]).loc[mk] * 100).values          # in Prozentpunkten
    zentriert = d - np.median(d)
    for delta in (0.0, 0.5, 1.0, 1.5, 2.0):
        treffer = 0
        for _ in range(N):
            s = rng.choice(zentriert, size=len(d), replace=True) + delta
            if np.allclose(s, 0): continue
            treffer += wilcoxon(s).pvalue < 0.05
        zeilen.append(dict(modell=name, streuung_sd=d.std(ddof=1), delta_pp=delta, anteil_signifikant=treffer / N))
t = pd.DataFrame(zeilen)
t.to_csv(ROOT / "results/tables/trennschaerfe.csv", index=False, float_format="%.4f")
print(t.pivot(index="modell", columns="delta_pp", values="anteil_signifikant").round(3).to_string())
print(t.groupby("modell").streuung_sd.first().round(2).to_string())
