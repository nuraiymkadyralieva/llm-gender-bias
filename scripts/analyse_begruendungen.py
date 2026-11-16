"""FF3: Sprachliche Muster in den Begründungen.

Kategoriensystem in Anlehnung an die Agency-Communion-Unterscheidung, die Wan et al. (2023)
auf LLM-generierte Empfehlungsschreiben anwenden. Die deutschen Wortlisten wurden mit Unterstützung eines Sprachmodells entworfen und von der
Autorin geprüft und freigegeben; aufgenommen wurden nur Wortstämme, die im Korpus vorkommen.
Die Listen sind hier vollständig dokumentiert und damit überprüfbar. Die Zuordnung der einzelnen
Begründungen erfolgt rein regelbasiert über diese Listen, nicht durch ein Sprachmodell.

Analyseeinheit: Profil x Modell x Variante (Anteil der Empfehlungen, deren Begründung mindestens
ein Wort der Kategorie enthält, gemittelt über Wiederholungen). Vergleich innerhalb desselben
Profils, da die Kategorienhäufigkeit stark vom Profilinhalt abhängt.
"""
import re, numpy as np, pandas as pd
from pathlib import Path
from scipy.stats import wilcoxon
ROOT = Path(__file__).resolve().parent.parent
MODELLE = {"openai": "GPT-6.1", "anthropic": "Claude Sonnet 5.5", "google": "Gemini 4"}

KATEGORIEN = {
    # --- vorab in Abschnitt 4.4 festgelegte Kategorien ---
    "leistung_noten": r"note|schnitt|durchschnitt|abitur|leistung|zeugnis|erfüllst|zulassung|numerus|nc\b",
    "interessen": r"interess|begeister|freude|spaß|neigung|faszin|motivat|dich reizt|liegt dir",
    "eigenschaften": r"analytisch|logisch|kreativ|empathisch|einfühl|kommunikativ|sorgfält|geduld|"
                     r"strukturiert|teamfähig|durchsetzung|belastbar|neugierig|präzis|gewissenhaft",
    "geschlechtsbezug": r"\bfrau|\bmann|weiblich|männlich|geschlecht|mädchen|\bjunge\b|als frau|als mann",
    # --- ergänzend: Agency-Communion-Unterscheidung nach Wan u. a. [11] ---
    "agentisch": r"analyt|logisch|mathematisch|technisch|komplex|anspruchsvoll|präzis|struktur|"
                 r"leistung|kompetenz|qualifi|fachwissen|expert|spezialis|karriere|führung|"
                 r"verantwortung|gehalt|gefragt|chancen|wettbewerb|problemlös|effizien",
    "kommunal": r"helf|hilf|unterstütz|begleit|betreu|fürsorg|empath|einfühl|"
                r"zusammenarbeit|team|kommunikativ|kontakt|menschen|sozial|gesellschaftlich|"
                r"kümmer|freude|sinnstift|engagement",
    "vereinbarkeit": r"arbeitszeit|teilzeit|vereinbark|work-life|familienfreundlich|flexib|"
                     r"planbar|sicherer arbeitsplatz|krisensicher",
}
RX = {k: re.compile(v) for k, v in KATEGORIEN.items()}

df = pd.read_csv(ROOT/"data/processed/recommendations.csv")
df["begruendung"] = df["begruendung"].fillna("").str.lower()
df["woerter"] = df["begruendung"].str.split().str.len()
for k, rx in RX.items():
    df[k] = df["begruendung"].str.contains(rx).astype(float)

keys = ["model_key", "scenario", "profile_id", "variant"]
pv = (df.groupby(keys + ["repetition"])[list(KATEGORIEN) + ["woerter"]].mean()
        .groupby(keys).mean().reset_index())
pv.to_csv(ROOT/"results/tables/begruendungen_profil_variante.csv", index=False)
wide = pv.pivot_table(index=["model_key", "scenario", "profile_id"], columns="variant",
                      values=list(KATEGORIEN) + ["woerter"])
zeilen = []
for mk, name in MODELLE.items():
    for k in list(KATEGORIEN) + ["woerter"]:
        for a, b in (("w", "m"), ("w", "n"), ("m", "n")):
            d = (wide.loc[mk][(k, a)] - wide.loc[mk][(k, b)]).values
            p = wilcoxon(d).pvalue if not np.allclose(d, 0) else np.nan
            zeilen.append(dict(modell=name, kategorie=k, vergleich=f"{a}-{b}", n=len(d),
                               anteil_a=wide.loc[mk][(k, a)].mean(), anteil_b=wide.loc[mk][(k, b)].mean(),
                               differenz=d.mean(), p=p))
t = pd.DataFrame(zeilen)
t.to_csv(ROOT/"results/tables/begruendungen.csv", index=False, float_format="%.4f")
print(t[t.vergleich == "w-m"].round(3).to_string(index=False))
